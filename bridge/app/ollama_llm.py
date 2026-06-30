"""
Ollama chat client (text + vision).

The bridge uses Ollama for two things:
  - Text chat (qwen3.5:397b-cloud or similar)
  - Vision frames (llava:7b — supports image inputs)

The Gemini Bidi protocol doesn't separate these — both audio and video
frames come over the same WebSocket as `realtimeInput` messages. Inside
the bridge, we accumulate audio chunks until VAD-style activity detection
fires (TBD), then transcribe via Speaches, send the text + latest video
frame to Ollama in a chat request, and stream the response back as audio.
"""

from __future__ import annotations

import base64
import logging
from typing import Any
import httpx
from .config import settings

log = logging.getLogger(__name__)


async def chat_text(messages: list[dict[str, Any]], system: str | None = None) -> str:
    """
    Send a text-only chat to Ollama. Returns the assistant's reply text.

    messages: list of {"role": "user"|"assistant"|"system", "content": "..."}
    """
    payload_messages = []
    if system:
        payload_messages.append({"role": "system", "content": system})
    payload_messages.extend(messages)

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{settings.ollama_url}/api/chat",
            json={
                "model": settings.ollama_chat_model,
                "messages": payload_messages,
                "stream": False,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "")


async def chat_with_image(
    text: str,
    image_jpeg_bytes: bytes,
    system: str | None = None,
) -> str:
    """
    Send text + a single image to Ollama's vision model (llava:7b).
    Returns the assistant's reply text.
    """
    image_b64 = base64.b64encode(image_jpeg_bytes).decode("ascii")
    payload_messages = []
    if system:
        payload_messages.append({"role": "system", "content": system})
    payload_messages.append({
        "role": "user",
        "content": text,
        "images": [image_b64],
    })

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{settings.ollama_url}/api/chat",
            json={
                "model": settings.ollama_vision_model,
                "messages": payload_messages,
                "stream": False,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "")


def encode_base64_image(jpeg_bytes: bytes) -> str:
    return base64.b64encode(jpeg_bytes).decode("ascii")


def decode_base64_image(b64: str) -> bytes:
    return base64.b64decode(b64)
