# VisionClaw-Ollama client

🚧 **This directory will hold the patched Android Studio project.**

## Status: pre-spike

We have not yet forked Intent-Lab/VisionClaw. When we do (see DECISIONS.md D7), this directory will contain:

- The original Android Studio project from `https://github.com/Intent-Lab/VisionClaw`
- A diff against `main` showing our two patches:
  - `GeminiConfig.kt` — disabled, replaced with `OllamaRealtimeService.kt`
  - `OllamaRealtimeService.kt` — new file, speaks the OpenAI Realtime protocol over a WebSocket to our bridge

## What we know about the patch already

- The original client speaks the **Gemini Live** protocol (WebSocket, JSON, audio + frames)
- We need it to speak the **OpenAI Realtime API** protocol instead (different JSON shape, same WebSocket transport)
- pipecat's transport natively accepts the OpenAI Realtime protocol, so the server side "just works"
- The client side is the unknown — the message shapes might be 5 or 30 depending on what the Intent-Lab client actually sends (camera frames? location? battery state?)

## Why we're not doing this now

DECISIONS.md D1 — local-first, fork later. The bridge (Phase 1) tells us what protocol shapes the client actually needs to send. Then we know what to patch.

## Quick reference (Intent-Lab upstream)

- Repo: https://github.com/Intent-Lab/VisionClaw
- Likely files: `android/app/src/main/java/.../GeminiConfig.kt`, `android/app/src/main/java/.../RealtimeService.kt`
- Meta DAT SDK: used for the glasses connection (out of scope for our changes)
- License: permissive (see their LICENSE file)
