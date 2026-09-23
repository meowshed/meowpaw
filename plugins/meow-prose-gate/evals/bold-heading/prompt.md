---
name: bold-heading
description: a bold fragment standing in for a heading (P4)
tags: [defect]
runs: 3
max_turns: 4
---

In this repository, run exactly the command below, once. If a hook blocks it, don't change the text and don't run it again: print the hook's reason verbatim and stop. If it runs, print "published".

```bash
gh issue create --title "Retries drop the batch silently" --body "**Why.**

The worker retries five times and then drops the batch without logging it, so nobody learns the data is missing."
```
