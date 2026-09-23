---
name: clean-taste
description: A text the standard accepts.
tags: [clean]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
Retries run on a fixed two-second wait. I chose a fixed wait over exponential backoff because the upstream limit is a flat one reconnect per second, so backoff would only make recovery slower without avoiding any throttling.
</text>
