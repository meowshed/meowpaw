---
name: rule-t4-two-words-for-one-thing
description: A text carrying a named defect.
tags: [defect, rule-T4]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
The scheduler hands each job to a worker. When a task fails, the scheduler retries the unit of work three times. A job that fails the third time goes to the dead-letter queue, and the task is dropped.
</text>
