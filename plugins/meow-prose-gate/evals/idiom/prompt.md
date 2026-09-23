---
name: idiom
description: an idiom, 'low-hanging fruit' (P1)
tags: [defect]
runs: 3
max_turns: 4
---

In this repository, run exactly the command below, once. If a hook blocks it, don't change the text and don't run it again: print the hook's reason verbatim and stop. If it runs, print "published".

```bash
git commit --allow-empty -m "Cache rendered pages" -m "Caching is the low-hanging fruit here, so the server skips the template step on a repeat request."
```
