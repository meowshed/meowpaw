---
name: rule-s2-pull-request-with-bold-labels
description: A text carrying a named defect.
tags: [defect, rule-S2]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
**What changed**
The importer now skips empty lines.

**Why**
Empty lines made it stop.

**Testing**
Tested locally.
</text>
