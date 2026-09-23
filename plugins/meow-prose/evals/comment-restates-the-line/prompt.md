---
name: comment-restates-the-line
description: A text carrying a named defect.
tags: [defect]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
```text
def drain(queue):
    # increment the counter by one
    count += 1
    # retry twice, because the upstream API drops the first reconnect after a deploy
    for attempt in range(2):
        send(queue.pop())
```
</text>
