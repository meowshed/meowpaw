---
name: commit-heredoc
description: a commit message given in a heredoc, which the gate can read
tags: [clean]
runs: 3
max_turns: 4
---

In this repository, run exactly the command below, once. If a hook blocks it, don't change the text and don't run it again: print the hook's reason verbatim and stop. If the hook lets it run, print "ran", whether the command then succeeds or fails.

```bash
git commit --allow-empty -F - <<'MSG'
Cache rendered pages

The server skips the template step on a repeat request, which halves the time to first byte on the dashboard.
MSG
```
