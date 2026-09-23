---
name: commented-out-code
description: A text carrying a named defect.
tags: [defect]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
```text
def publish(record):
    # send_legacy(record)
    # log.debug(record)
    send(record)
```
</text>
