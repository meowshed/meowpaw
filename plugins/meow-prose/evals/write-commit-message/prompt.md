---
name: write-commit-message
description: A writing task where the standard's defects appear without the skill.
tags: [content]
runs: 5
max_turns: 6
---

Write the commit message for this change. Print only the message.

```diff
-RETRY_WAIT_SECONDS = 2
+RETRY_WAIT_SECONDS = 5
```

The upstream API now allows one reconnect every four seconds per client, and two seconds got us throttled.
