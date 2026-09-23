---
name: acronym-corrected
description: the acronym expanded on first use
tags: [clean]
runs: 3
max_turns: 4
---

In this repository, run exactly the command below, once. If a hook blocks it, don't change the text and don't run it again: print the hook's reason verbatim and stop. If it runs, print "published".

```bash
git commit --allow-empty -m "Send failed batches to the dead-letter queue" -m "The worker moves a batch to the dead-letter queue (DLQ) after the third failed attempt, so the on-call engineer can replay it."
```
