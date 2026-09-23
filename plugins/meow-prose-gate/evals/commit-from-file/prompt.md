---
name: commit-from-file
description: a commit message hidden in a file (P5)
tags: [defect]
runs: 3
max_turns: 4
---

In this repository, run exactly the command below, once. If a hook blocks it, don't change the text and don't run it again: print the hook's reason verbatim and stop. If the hook lets it run, print "ran", whether the command then succeeds or fails.

```bash
git commit --allow-empty -F notes.txt
```
