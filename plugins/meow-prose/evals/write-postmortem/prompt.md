---
name: write-postmortem
description: A writing task where the standard's patterns appear without the skill.
tags: [content, patterns]
runs: 5
max_turns: 6
---

Write a short postmortem for the team. On 2026-09-23 the importer loaded the same partner file twice, because the retry after a network timeout did not check whether the first load had committed. 1,200 duplicate rows reached the warehouse and the finance dashboard double-counted revenue for four hours. We added an idempotency key per file. Print only the postmortem.
