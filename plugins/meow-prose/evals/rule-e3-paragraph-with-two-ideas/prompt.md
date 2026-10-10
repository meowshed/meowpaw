---
name: rule-e3-paragraph-with-two-ideas
description: A text carrying a named defect.
tags: [defect, rule-E3]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
# Operating the worker

## Logs and retries

The worker writes one JSON line per job, with the job identifier, the start time and the outcome. Failed jobs are retried three times with a delay that doubles each time, starting at two seconds. The log file rotates at 100 MB. A job that fails the third time moves to the dead-letter queue, where it stays for seven days. Logs older than 30 days are deleted by the nightly task.
</text>
