# VisionClaw-Ollama bridge

🚧 **Phase 1 spike. Not implemented yet.**

The bridge is a FastAPI app that:

1. Accepts a WebSocket connection from the Android client on `/v1/realtime`
2. Speaks the **OpenAI Realtime API** protocol (JSON messages, audio in/out, tool calls)
3. Internally runs a **pipecat pipeline** that:
   - STT: Speaches (192.168.4.12:8000) — audio chunk → text
   - LLM: Ollama (localhost:11434) — text + vision frames → text
   - TTS: Piper or Speaches TTS (TBD at spike time) — text → audio
4. Forwards tool calls to OpenClaw's existing tool-use layer (not directly to MCP)

## Planned file layout

```
bridge/
├── pyproject.toml          — deps: fastapi, uvicorn, websockets, pipecat-ai, ollama, httpx
├── README.md               — this file
├── app/
│   ├── __init__.py
│   ├── main.py             — FastAPI entry, WebSocket route
│   ├── pipeline.py         — pipecat pipeline assembly
│   ├── ollama_stt.py       — STT adapter (Speaches → text)
│   ├── ollama_llm.py       — LLM adapter (Ollama chat → text)
│   ├── ollama_tts.py       — TTS adapter (text → audio)
│   ├── protocol.py         — OpenAI Realtime message shape (pydantic models)
│   ├── tools.py            — tool-call forwarding to OpenClaw
│   └── config.py           — env vars, service URLs
└── tests/
    ├── test_protocol.py    — message shape roundtrip
    └── test_pipeline.py    — mock STT/LLM/TTS, verify pipeline shape
```

## Spike success criteria (Phase 1 done)

End of Phase 1: I can `wscat` into the bridge and get a response.

```bash
# Terminal 1: start the bridge
cd bridge/
python -m venv .venv && source .venv/bin/activate
pip install -e .
python -m app.main

# Terminal 2: smoke test
wscat -c ws://localhost:7860/v1/realtime
> {"type": "session.update", "session": {"voice": "default"}}
< {"type": "session.created", "session": {"id": "...", ...}}

> {"type": "conversation.item.create", "item": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "hello"}]}}
> {"type": "response.create"}
< {"type": "response.audio.delta", "delta": "..."}
```

When that roundtrip works, Phase 1 is done. We then move to Phase 2 (client patch).

## Service dependencies

- **Speaches STT**: `http://192.168.4.12:8000` (Jetson, already deployed)
- **Ollama**: `http://localhost:11434` (same host as the bridge, already deployed)
- **OpenClaw tool-use**: `http://localhost:18789` (existing gateway, TBD how to call into it)
- **TTS**: TBD — Piper or Speaches TTS, whichever the spike shows works

## Configuration

The bridge will read from `/home/juan/.openclaw/workspace/.env`:

```bash
SPEACHES_URL=http://192.168.4.12:8000
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:14b           # TBD at spike time
OPENCLAW_GATEWAY_URL=http://localhost:18789
BRIDGE_HOST=0.0.0.0
BRIDGE_PORT=7860
```

The model choice is open — for realtime we want something fast. `qwen2.5:14b` is a starting point but we'll measure.

## Punted to spike time

- Vision frame handling (probably a custom message type on top of OpenAI Realtime)
- Tool-call message shape (depends on what the client actually sends)
- TTS choice (depends on whether we can stream audio back fast enough)
- Auth (probably none for LAN, but reconsider for the public-facing cloudflared tunnel)
- Whether to add `/health` and `/metrics` endpoints (yes, but cheap)
