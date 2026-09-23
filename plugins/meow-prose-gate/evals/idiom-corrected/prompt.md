---
name: idiom-corrected
description: the idiom replaced by a literal statement
tags: [clean]
runs: 3
max_turns: 4
---

In this repository, run exactly the command below, once. If a hook blocks it, don't change the text and don't run it again: print the hook's reason verbatim and stop. If the hook lets it run, print "ran", whether the command then succeeds or fails.

```bash
git commit --allow-empty -m "Cache rendered pages" -m "Caching is the cheapest fix here, so the server skips the template step on a repeat request."
```
