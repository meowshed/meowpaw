---
name: rule-a2-warning-after-the-step
description: A text carrying a named defect.
tags: [defect, rule-A2]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
To free disk space, stop the service and run `rm -rf data/cache`. This deletes every cached report, and the next build takes an hour to refill it. Then start the service again.
</text>
