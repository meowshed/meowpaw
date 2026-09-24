---
name: write-bug-issue
description: A writing task where the standard's defects appear without the skill.
tags: [content]
runs: 5
max_turns: 6
---

Write a GitHub issue: worker.py retries a failed batch five times and then drops it without logging anything, so nobody learns the data is missing. I expected it to log the batch ID and move the batch to a dead-letter queue. To reproduce: point it at a stopped database and run `python3 worker.py --once`. Print only the issue.
