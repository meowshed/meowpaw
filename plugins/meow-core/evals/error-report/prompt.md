---
name: error-report
description: A failing deploy, reported back to the person who has to fix it.
tags: [reporting]
runs: 3
max_turns: 10
expected_outcome: The reply opens with the failure, names the file and the line, and says what would fix it, with no expression of dismay in front of it.
---

The deploy stopped and this is all I have:

```text
$ deployctl apply --env staging
reading deploy.toml
validating 14 settings
error: deploy.toml:27: `retries` must be a whole number between 0 and 10, got "three"
aborted: nothing was applied
```

What happened?
