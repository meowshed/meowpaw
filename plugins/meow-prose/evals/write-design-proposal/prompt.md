---
name: write-design-proposal
description: A writing task where the standard's defects appear without the skill.
tags: [content]
runs: 5
max_turns: 6
---

Write a one-page design proposal for caching the rendered dashboard pages. Readers are the platform team, who will decide whether to fund it. The cache would cut page render time from 900 ms to about 80 ms, costs one more Redis instance, and serves pages up to 60 seconds stale. Print only the proposal in Markdown.
