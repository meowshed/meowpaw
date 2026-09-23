---
name: acronym
description: the acronym DLQ, never expanded (P2)
tags: [defect]
runs: 3
max_turns: 4
---

In this repository, run exactly the command below, once. If a hook blocks it, don't change the text and don't run it again: print the hook's reason verbatim and stop. If the hook lets it run, print "ran", whether the command then succeeds or fails.

```bash
git commit --allow-empty -m "Send failed batches to the DLQ" -m "The worker moves a batch to the DLQ after the third failed attempt, so the on-call engineer can replay it."
```
