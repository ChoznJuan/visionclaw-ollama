# VisionClaw-Ollama client

🚧 **No client modifications needed in Phase 1 — the bridge speaks the same Gemini Bidi protocol the upstream client already speaks.**

## Status: **D3 changed on 2026-06-30**

The original plan was to patch the Android sample (GeminiConfig.kt + new OllamaRealtimeService.kt) to speak the OpenAI Realtime protocol. **We changed our minds after reading the actual upstream code:**

- The Android sample already speaks **Gemini BidiGenerateContent** over WebSocket (see `samples/CameraAccessAndroid/.../gemini/GeminiLiveService.kt`)
- The bridge speaks the same protocol
- The only config change on the client is pointing the WebSocket URL at our bridge (instead of `generativelanguage.googleapis.com`) and skipping the API key check

**What this means:** when we eventually patch the client, it's a 5-line change in `GeminiConfig.kt` to point at `ws://192.168.4.X:7860/v1/realtime`. We don't need to write a new service class or change the protocol.

## Future patches (if any)

If we ever need to diverge from the upstream protocol (e.g. add a custom message type for OpenClaw tool calls), this directory will hold:

- The original Android Studio project from `https://github.com/Intent-Lab/VisionClaw`
- A diff against `main` showing our (minimal) patches
- Notes on which Android Studio / Kotlin / Gradle versions are needed to build the sample

## Quick reference (Intent-Lab upstream)

- Repo: https://github.com/Intent-Lab/VisionClaw
- Android sample: `samples/CameraAccessAndroid/`
- Key files:
  - `gemini/GeminiConfig.kt` — WebSocket URL, model name, audio config
  - `gemini/GeminiLiveService.kt` — the actual WebSocket client
- Meta DAT SDK: used for the glasses connection (out of scope for our changes)
- License: Meta Wearables DAT Terms (see upstream LICENSE)
