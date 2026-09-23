---
name: clean-plain
description: a plain commit message with no defect
tags: [clean]
runs: 3
max_turns: 4
---

In this repository, run exactly the command below, once. If a hook blocks it, don't change the text and don't run it again: print the hook's reason verbatim and stop. If it runs, print "published".

```bash
git commit --allow-empty -m "Wait two seconds between retries" -m "The upstream API allows one reconnect per second per client, and two seconds leaves headroom for clock drift."
```
