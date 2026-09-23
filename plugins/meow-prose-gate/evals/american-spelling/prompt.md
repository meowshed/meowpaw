---
name: american-spelling
description: American spellings 'Normalize' and 'behavior' in prose (P3)
tags: [defect]
runs: 3
max_turns: 4
---

In this repository, run exactly the command below, once. If a hook blocks it, don't change the text and don't run it again: print the hook's reason verbatim and stop. If the hook lets it run, print "ran", whether the command then succeeds or fails.

```bash
git commit --allow-empty -m "Normalize the retry behavior" -m "The worker now waits two seconds between retries, which matches the behavior the upstream API documents."
```
