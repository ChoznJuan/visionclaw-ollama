# VisionClaw-Ollama docs

🚧 **Empty for now.** Will hold:

- Protocol traces from the spike (raw WebSocket frames between client and bridge)
- Spike results (what worked, what didn't, what we changed our minds about)
- Architecture decision records (ADRs) for changes from the DECISIONS.md baseline
- Performance measurements (latency, model choice, frame rate)

## What gets logged here

- Every spike's `wscat` session, captured to a `.txt` file
- Every decision we change our minds about (and why)
- Every model we test and the latency/quality tradeoffs
- Every protocol message we don't understand (so we can come back to it)

## Convention

One file per topic. Filename = kebab-case topic name. Date in frontmatter if relevant.
