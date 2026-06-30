# LICENSE-NOTES — VisionClaw-Ollama

This repo is a **public fork** of [Intent-Lab/VisionClaw](https://github.com/Intent-Lab/VisionClaw), which has no open-source license. This file explains what that means and what we can/cannot do with the code.

## TL;DR

- **We cannot (and do not) claim a permissive license on this repo.** No MIT, no Apache, no BSD.
- **We can use, modify, and run the code** for personal projects under Meta's Wearables Device Access Toolkit Terms (which are the upstream's "LICENSE" file).
- **We cannot redistribute the code** as if it were open-source without Meta's written permission.
- **Public visibility on GitHub is fine** — GitHub's Terms of Service grants view-only access to public repos. Forking is allowed. Modifying for personal use is allowed.
- **If this work ever becomes something we want to share more broadly**, we'd need to:
  1. Get Meta's permission, OR
  2. Reimplement from scratch (not a fork) under our own license, OR
  3. Extract only the parts that aren't derivative of the upstream code (probably: the bridge, since that's our original work) and ship those separately

## What the upstream license actually says

The `LICENSE` file in the upstream repo (preserved here verbatim from the merge) is the **Meta Wearables Device Access Toolkit Terms** (linked to https://wearables.developer.meta.com/terms). Key points:

- You can use the Wearables DAT SDK to build apps for Meta's smart glasses
- You agree to Meta's Acceptable Use Policy
- Meta can revoke your access if you violate the terms
- It's a **terms-of-service agreement**, not an open-source license

## What this means for the project

| Action | Allowed? | Notes |
|---|---|---|
| Build a private/local app | ✅ | Standard Meta DAT usage |
| Fork for personal use | ✅ | GitHub TOS + Meta DAT terms |
| Public visibility on GitHub | ✅ | Anyone with the URL can see the code; that's GitHub's model |
| Modify the upstream code | ✅ | Standard fork behavior |
| Reimplement the same idea from scratch | ✅ | No derivative claim if we don't copy code |
| Add a permissive LICENSE file to this repo | ❌ | We don't own the rights to grant that |
| Redistribute the binary/source under MIT/Apache | ❌ | Would violate upstream terms |
| Use in a commercial product | ❓ | Likely needs Meta partnership |
| Claim ownership of the upstream code | ❌ | Attribution required |

## Why we're keeping the upstream LICENSE and NOTICE files

The upstream `LICENSE` (Meta Wearables DAT Terms) and `NOTICE` (attribution file) are kept in the merge history. They are **Meta's terms**, not ours — removing them would be misrepresenting the source. Future maintainers of this repo: leave them alone.

## What the bridge is and isn't

The `bridge/` directory is **our original work** — pipecat + Ollama + Speaches + FastAPI WebSocket. If we ever want to release the bridge under a permissive license, we could:

- Move it to a separate repo (`ChoznJuan/realtime-bridge` or similar)
- Strip any non-permissive code that was copied from upstream
- License the result under MIT/Apache

That's a future-Juan problem. For now, the bridge lives in this repo and inherits the upstream license posture.

## Decisions log

- **D7** in `DECISIONS.md` records the 2026-06-30 decision to keep this repo **public** (changed from the original "private" plan in the recap) due to GitHub's "public forks can't be made private" rule.
- **2026-06-30** the LICENSE-NOTES.md was added after we discovered the upstream had no open-source license.
