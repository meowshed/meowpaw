---
name: clean-taste
description: A text the standard accepts.
tags: [clean]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
Retries wait a fixed two seconds. I chose a fixed wait over exponential backoff because the upstream API documents a limit of one retry per second per client, so backoff would slow recovery and meet the same limit.
</text>
