"""
FastAPI app entry point for the VisionClaw-Ollama bridge.

Exposes:
  - GET  /health        — liveness check
  - GET  /v1/status     — service reachability (Ollama, Speaches)
  - WS   /v1/realtime   — Gemini BidiGenerateContent-compatible WebSocket endpoint
                          (same protocol the upstream Android client speaks)

Phase 1 success criterion (from bridge/README.md):
  wscat -c ws://localhost:7860/v1/realtime
  > {"setup": {...}}
  < {"setupComplete": {}}
  > {"realtimeInput": {"audio": {"mimeType": "audio/pcm;rate=16000", "data": "<base64>"}}}
  > {"realtimeInput": {"video": {"mimeType": "image/jpeg", "data": "<base64>"}}}
  < {"serverContent": {"modelTurn": {"parts": [{"inlineData": {"mimeType": "audio/pcm;rate=24000", "data": "<base64>"}}]}, "turnComplete": true}}
"""

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import httpx
import uvicorn

from .config import settings
from . import ollama_stt, ollama_llm, tools

log = logging.getLogger("bridge")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    log.info("Bridge starting on %s:%d", settings.bridge_host, settings.bridge_port)
    log.info("  Ollama:    %s (chat=%s, vision=%s)", settings.ollama_url, settings.ollama_chat_model, settings.ollama_vision_model)
    log.info("  Speaches:  %s (stt=%s, tts=%s)", settings.speaches_url, settings.speaches_stt_model, settings.speaches_tts_model)
    log.info("  OpenClaw:  %s (Phase 2)", settings.openclaw_gateway_url)
    yield
    log.info("Bridge shutting down")


app = FastAPI(title="VisionClaw-Ollama Bridge", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/v1/status")
async def status():
    """Check reachability of Ollama and Speaches."""
    results = {}
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            r = await client.get(f"{settings.ollama_url}/api/tags")
            results["ollama"] = {"reachable": True, "status_code": r.status_code}
        except Exception as e:
            results["ollama"] = {"reachable": False, "error": str(e)}
        try:
            r = await client.get(f"{settings.speaches_url}/v1/models")
            results["speaches"] = {"reachable": True, "status_code": r.status_code}
        except Exception as e:
            results["speaches"] = {"reachable": False, "error": str(e)}
    return results


@app.websocket("/v1/realtime")
async def realtime_endpoint(websocket: WebSocket):
    """
    Gemini BidiGenerateContent WebSocket endpoint.

    Protocol (per upstream's GeminiLiveService.kt):
      Client → Server:
        {"setup": {model, generationConfig, systemInstruction, tools?, ...}}
        {"realtimeInput": {"audio": {mimeType, data}}}     # base64 PCM
        {"realtimeInput": {"video": {mimeType, data}}}     # base64 JPEG
        {"clientContent": {"turns": [{"role": "user", "parts": [{"text": "..."}]}], "turnComplete": true}}
        {"toolResponse": {"functionResponses": [...]}}
      Server → Client:
        {"setupComplete": {}}
        {"serverContent": {"modelTurn": {"parts": [{"inlineData": {"mimeType": "audio/pcm;rate=24000", "data": "..."}}]}, "turnComplete": true}}
        {"serverContent": {"inputTranscription": {"text": "..."}}}
        {"serverContent": {"outputTranscription": {"text": "..."}}}
        {"toolCall": {"functionCalls": [{"name": "..."}, "args": {...}, "id": "..."}]}}
    """
    await websocket.accept()
    log.info("WebSocket connected: %s", websocket.client)

    # Session state
    audio_buffer = bytearray()
    last_video_jpeg: bytes | None = None
    conversation: list[dict] = []
    system_prompt: str = "You are a helpful assistant on Meta Ray-Ban smart glasses. Be concise."

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError as e:
                log.warning("Bad JSON from client: %s", e)
                continue

            # ----- 1. setup -----
            if "setup" in msg:
                setup = msg["setup"]
                system_prompt = setup.get("systemInstruction", {}).get("parts", [{}])[0].get("text", system_prompt)
                log.info("Setup complete. System: %r", system_prompt[:80])
                await websocket.send_text(json.dumps({"setupComplete": {}}))
                continue

            # ----- 2. realtimeInput: audio chunk -----
            if "realtimeInput" in msg:
                ri = msg["realtimeInput"]
                if "audio" in ri:
                    pcm = ollama_stt.decode_base64_audio(ri["audio"]["data"])
                    audio_buffer.extend(pcm)
                    # TODO(phase-2): VAD — when user stops speaking, flush audio_buffer
                    # through Speaches STT, get text, add to conversation, send to Ollama
                    # with the latest video frame.
                    log.debug("Audio chunk: %d bytes (buffer: %d)", len(pcm), len(audio_buffer))
                if "video" in ri:
                    last_video_jpeg = ollama_llm.decode_base64_image(ri["video"]["data"])
                    log.debug("Video frame: %d bytes", len(last_video_jpeg))
                continue

            # ----- 3. clientContent: explicit text turn -----
            if "clientContent" in msg:
                turn_text = ""
                for turn in msg["clientContent"].get("turns", []):
                    for part in turn.get("parts", []):
                        if "text" in part:
                            turn_text += part["text"]
                if not turn_text:
                    continue

                log.info("User turn: %r", turn_text[:120])
                # Echo back as input transcription (matches Gemini behavior)
                await websocket.send_text(json.dumps({
                    "serverContent": {
                        "inputTranscription": {"text": turn_text}
                    }
                }))

                # Decide: text-only chat, or vision-augmented chat
                if last_video_jpeg:
                    assistant_text = await ollama_llm.chat_with_image(
                        text=turn_text,
                        image_jpeg_bytes=last_video_jpeg,
                        system=system_prompt,
                    )
                else:
                    conversation.append({"role": "user", "content": turn_text})
                    assistant_text = await ollama_llm.chat_text(
                        messages=conversation,
                        system=system_prompt,
                    )
                    conversation.append({"role": "assistant", "content": assistant_text})

                log.info("Assistant: %r", assistant_text[:120])

                # Echo back as output transcription
                await websocket.send_text(json.dumps({
                    "serverContent": {
                        "outputTranscription": {"text": assistant_text}
                    }
                }))

                # Synthesize audio (Phase 1: serialize; Phase 2: stream)
                try:
                    audio_out = await ollama_stt.synthesize_speech(assistant_text)
                    audio_b64 = ollama_stt.encode_base64_audio(audio_out)
                    await websocket.send_text(json.dumps({
                        "serverContent": {
                            "modelTurn": {
                                "parts": [{
                                    "inlineData": {
                                        "mimeType": f"audio/pcm;rate={settings.output_audio_sample_rate}",
                                        "data": audio_b64,
                                    }
                                }]
                            },
                            "turnComplete": True,
                        }
                    }))
                except Exception as e:
                    log.error("TTS failed (returning text only): %s", e)
                    # Still mark turn complete so client knows we're done
                    await websocket.send_text(json.dumps({
                        "serverContent": {"turnComplete": True}
                    }))
                continue

            # ----- 4. toolResponse -----
            if "toolResponse" in msg:
                # Phase 1: tool responses are acked but not processed (the LLM
                # doesn't actually call tools yet because we don't expose any
                # real ones in the setup message).
                log.info("Tool response received (stub): %s", msg["toolResponse"])
                continue

            log.warning("Unknown message type: %s", list(msg.keys()))

    except WebSocketDisconnect:
        log.info("WebSocket disconnected: %s", websocket.client)
    except Exception as e:
        log.exception("WebSocket error: %s", e)
        try:
            await websocket.close(code=1011, reason=str(e))
        except Exception:
            pass


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.bridge_host,
        port=settings.bridge_port,
        log_level=settings.log_level.lower(),
    )
