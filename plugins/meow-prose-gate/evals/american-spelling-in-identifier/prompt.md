---
name: american-spelling-in-identifier
description: an American spelling only inside identifiers, which keep their own spelling
tags: [clean]
runs: 3
max_turns: 4
---

In this repository, run exactly the command below, once. If a hook blocks it, don't change the text and don't run it again: print the hook's reason verbatim and stop. If it runs, print "published".

```bash
git commit --allow-empty -m "Rename the colour setting" -m "The setting was called \`backgroundColor\` in the config, and now matches the \`color\` key the theme library reads."
```
