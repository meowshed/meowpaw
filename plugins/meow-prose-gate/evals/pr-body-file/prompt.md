---
name: pr-body-file
description: a pull request body hidden in a file (P5)
tags: [defect]
runs: 3
max_turns: 4
---

In this repository, run exactly the command below, once. If a hook blocks it, don't change the text and don't run it again: print the hook's reason verbatim and stop. If it runs, print "published".

```bash
gh pr create --title "Cache rendered pages" --body-file body.md
```
