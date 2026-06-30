# DECISIONS — VisionClaw-Ollama

Why we did things, in case we (or future-us) need to re-debate.

## D1. Local-first, fork later

**Decision:** Don't fork Intent-Lab/VisionClaw until the bridge works end-to-end.

**Why:** Forking too early commits us to upstream-fork conventions (CLA, license headers, branch naming) before we know what we're shipping. The bridge is a fresh codebase anyway — no upstream value to preserve. Forking post-spike avoids paperwork fights and lets us learn the actual protocol shapes we need to commit to.

**When we revisit:** After the `wscat` end-to-end test passes (Phase 1 done).

## D2. pipecat as the bridge framework

**Decision:** Use [pipecat-ai](https://github.com/pipecat-ai/pipecat) for the bridge.

**Why:**
- pipecat ships a working **OpenAI Realtime API**-compatible WebSocket transport
- Native adapters for Ollama, Speaches, and Piper
- Pipeline composition is the right shape for STT → LLM → TTS → tool calls
- Python (matches the rest of OpenClaw, no new language on the stack)

**Alternatives considered:**
- *Raw FastAPI + asyncio + websockets*: more work, no pipeline primitives, we'd re-implement what pipecat already does
- *LiveKit Agents*: more opinionated, would drag in a LiveKit server dependency we don't need for a single client
- *DIY over the Gemini Live protocol*: would require us to fake the Gemini protocol, which is more brittle than speaking OpenAI Realtime

## D3. OpenAI Realtime protocol, not Gemini Live

**Decision:** The Android client will speak the OpenAI Realtime API protocol when pointed at our bridge.

**Why:**
- pipecat's transport speaks it natively
- The protocol is open, documented, and has 3+ open-source client implementations we can reference
- The Android client side of the patch is a known shape (5 message types in, ~5 out)
- Avoids the Meta DAT SDK + Gemini SDK relicense / re-architecture path

**Punted to fork-time:**
- Whether the protocol needs a custom serializer for vision frames (Gemini Live has dedicated frame messages; OpenAI Realtime is text-first and we'd add a `vision_frame` extension)
- Whether to upstream the protocol extension to OpenAI's spec or just ship our own

## D4. Speaches for STT, Ollama for LLM, Piper (later) for TTS

**Decision:** 
- STT: Speaches (already running on Jetson at 192.168.4.12:8000, faster-whisper-large-v3-turbo)
- LLM: Ollama (localhost:11434, the existing setup)
- TTS: **deferred to Phase 1 spike.** Piper or Speaches TTS, whichever we have working first.

**Why Speaches for STT:** Already deployed, already proven. Don't move what works.

**Why defer TTS:** Need to see what the bridge end-to-end test demands. If the client handles its own audio playback (likely, since Android has good audio APIs), the bridge might only need to return text or PCM chunks. Decide when we see it work.

## D5. Vision via frame upload, not streaming

**Decision:** Vision frames go over the WebSocket as base64-encoded images in a custom message, NOT as a live video stream.

**Why:**
- Meta Ray-Ban glasses already buffer and upload snapshots, not video
- LLM context windows don't need 30fps video
- Base64-in-JSON is fine for 1-2 frames per interaction
- Avoids a real-time video pipeline we don't need

**Punted:** Frame rate, max concurrent frames, what to do if the user takes a photo mid-conversation.

## D6. Tool calls go through OpenClaw, not directly to MCP

**Decision:** When the LLM wants to call a tool (e.g., "turn off the kitchen lights"), the bridge forwards it to OpenClaw's existing tool-use layer, not directly to MCP servers.

**Why:**
- OpenClaw already has tool routing, credential management, audit logging
- We don't want to maintain a parallel tool-call surface
- One source of truth for "what tools exist" stays in OpenClaw

**Punted:** Whether the bridge should expose its own MCP server for OpenClaw to call into. (Probably not — bridge is a service, not an agent.)

## D7. Public visibility (changed from private on 2026-06-30)

**Decision:** This repo is **public**, not private. Updated from the recap's "private" default after discussion.

**Why the change:** GitHub's policy is that public forks of public repos cannot be made private. Recreating via the import flow was an option, but Juan decided the simpler path (keep the public fork GitHub created automatically) was fine. The repo is a deliberate personal project; not gated behind private visibility.

**Current state (as of 2026-06-30):**
- Owner: `ChoznJuan`
- Repo: `visionclaw-ollama`
- Visibility: **public**
- Default branch: `main` only (other upstream branches — WebRTC, fastvlm, feature/*, lab — were deleted from the fork)
- Remote strategy: `origin` → fork (where we push), `upstream` → `https://github.com/Intent-Lab/VisionClaw.git` (where we track upstream changes)

**License note:** The upstream has no open-source license — the `LICENSE` file is just Meta's Wearables Device Access Toolkit terms, not a permissive license. This means:
- We can fork for personal use (GitHub's TOS grants view-only rights on public repos)
- We cannot strip Meta's LICENSE and replace it with MIT/Apache
- We should NOT add a `LICENSE` file claiming permissive terms
- A `LICENSE-NOTES.md` (TBD) should explain the relationship to upstream

**What we did at fork time:**
1. Forked `Intent-Lab/VisionClaw` to `ChoznJuan/visionclaw-ollama` (public, via GitHub API)
2. Deleted non-main branches from the fork: `WebRTC`, `fastvlm`, `feature/gaze-window-control`, `feature/mmduet2`, `feature/transcription`, `lab`
3. `git init` on `projects/visionclaw-ollama/`, added `origin` + `upstream` remotes
4. Merged upstream main into local (option 3a — full upstream history + our work on top)
5. First commit: scaffold (README, DECISIONS, bridge/, client/, docs/, scripts/)

## D8. The "memory gap" incident

**Decision:** A pre-dump hook on the 11 PM gateway restart is its own ticket. Don't conflate it with VisionClaw work.

**Why:** The fact that yesterday's VisionClaw conversation didn't make it to memory is a separate bug class (conversations lost on context rotation). VisionClaw should not block on fixing it, and the fix should not block on VisionClaw.

**Tracking:** Will add to `.learnings/LEARNINGS.md` and create a separate cron for the pre-dump hook this week.
