---
name: write-review-reply
description: A writing task where the standard's defects appear without the skill.
tags: [content]
runs: 5
max_turns: 6
---

A reviewer commented on my pull request: 'Why not just use the retry library we already depend on?' My reason: the library retries on every exception, including validation errors, which would re-send bad batches five times; ours retries only on connection errors. Write my reply to the reviewer. Print only the reply.
