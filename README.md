# VisionClaw-Ollama

Real-time AI assistant for Meta Ray-Ban smart glasses. **Voice + vision + agentic actions, all on-prem.**

This is a local-first fork/spike of [Intent-Lab/VisionClaw](https://github.com/Intent-Lab/VisionClaw). The upstream uses **Google Gemini Live** for realtime voice + vision. We're swapping that out for a **local Ollama + Speaches** pipeline so:

- Audio never leaves the LAN
- Vision frames never leave the LAN
- No Gemini API key, no quota, no per-minute cost
- Same UX, same Meta DAT SDK glasses, same OpenClaw tool-use — different brain

## Status

🚧 **Pre-spike.** No code yet. This README + DECISIONS.md is the design contract for what we build next.

| Phase | Goal | Status |
|---|---|---|
| 0 | Scaffold + design contract (this dir) | ✅ Done |
| 1 | `bridge/` — pipecat + Ollama + Speaches + FastAPI WebSocket, end-to-end with `wscat` | 🔜 Next session |
| 2 | `client/` — patch Intent-Lab's Android sample (GeminiConfig.kt + new OllamaRealtimeService.kt) to point at the bridge | ⏸ After 1 |
| 3 | Glasses → bridge → Ollama voice roundtrip on device | ⏸ After 2 |
| 4 | Already public at `ChoznJuan/visionclaw-ollama` (forked from Intent-Lab/VisionClaw) | ✅ Done |

## Architecture

```
┌────────────────────┐         ┌────────────────────────┐         ┌──────────────────┐
│  Meta Ray-Ban      │  WiFi   │  visionclaw-ollama/    │  HTTP   │  Ollama          │
│  glasses + Android │ ──────► │  bridge (FastAPI WS)   │ ──────► │  (local LLM)     │
│  client            │  audio  │  pipecat pipeline      │         │  + Speaches STT  │
│                    │ ◄────── │  OpenAI-realtime-      │ ◄────── │  + Piper TTS     │
│                    │  frames │  protocol-compatible   │         │  (later)         │
└────────────────────┘         └────────────────────────┘         └──────────────────┘
                                          │
                                          │  (vision + tool calls)
                                          ▼
                                ┌────────────────────────┐
                                │  OpenClaw agent        │
                                │  (existing)            │
                                └────────────────────────┘
```

## Why a separate "bridge" service

The Intent-Lab client speaks Google's Gemini Live protocol over a WebSocket. We're not re-implementing that — instead:

1. The bridge **emits the OpenAI Realtime API protocol** (which is much closer to what pipecat natively produces)
2. The Android client gets patched to **speak OpenAI Realtime** instead of Gemini Live when configured for our backend
3. The bridge translates between the protocol the Android client sends and the local Ollama/Speaches calls pipecat makes

This is the cheapest path because:
- pipecat ships a working OpenAI Realtime-compatible WebSocket transport
- OpenAI's protocol is well-documented and the Android client side is a known shape (~5 message types)
- We avoid the Meta DAT SDK upgrade / relicense path that came up yesterday

## Repo layout

```
visionclaw-ollama/
├── README.md         — this file
├── DECISIONS.md      — why we picked this architecture, what we punted
├── bridge/           — the FastAPI + pipecat + Ollama + Speaches service (Phase 1)
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py         — FastAPI entry, WebSocket route
│   │   ├── pipeline.py     — pipecat pipeline assembly
│   │   ├── ollama_stt.py   — STT adapter (Speaches → text)
│   │   ├── ollama_llm.py   — LLM adapter (Ollama chat → text)
│   │   ├── ollama_tts.py   — TTS adapter (text → audio)
│   │   └── protocol.py     — OpenAI Realtime message shape
│   └── tests/
├── client/           — Android Studio project (Phase 2)
│   └── README.md     — patch notes against Intent-Lab/VisionClaw
├── docs/             — design notes, protocol traces, spike results
└── scripts/          — dev helpers (start bridge, run wscat test, etc.)
```

## Local development

```bash
# 1. Install bridge deps (Phase 1, not yet implemented)
cd bridge/
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# 2. Start the bridge
python -m app.main    # listens on 0.0.0.0:7860

# 3. Smoke test with wscat (Phase 1 success criterion)
wscat -c ws://localhost:7860/v1/realtime
> {"type": "session.update", "session": {"voice": "default"}}
< {"type": "session.created", ...}
```

## Privacy

This project **exists because of** Juan's privacy principle. Every byte — audio in, frames in, audio out, tool calls out — stays on the LAN. No Gemini, no OpenAI, no Cloudflare. The bridge is the only thing the glasses talk to; the bridge is the only thing Ollama talks to; OpenClaw tool calls go over the existing self-hosted Nextcloud/Proxmox stack.

See [SOUL.md](../../../SOUL.md) for the broader principle.

## License

This repo is a **public fork of [Intent-Lab/VisionClaw](https://github.com/Intent-Lab/VisionClaw)**, which has no open-source license. The upstream `LICENSE` file is Meta's Wearables Device Access Toolkit terms, not a permissive license.

What that means here:
- **No permissive license applies.** We cannot (and do not) claim MIT/Apache/BSD on this repo.
- The upstream `LICENSE` and `NOTICE` files are kept verbatim, in the upstream history, for attribution.
- Our additions (`bridge/`, `client/` patches, the new `README.md`, `DECISIONS.md`) are released under the same terms as the upstream — Meta's Wearables DAT Terms + GitHub's view-only public access.
- See [`LICENSE-NOTES.md`](./LICENSE-NOTES.md) for the full breakdown of what we can and can't do with this code.
