---
name: write-revised-decision
description: A writing task where the standard's patterns appear without the skill.
tags: [content, patterns]
runs: 5
max_turns: 6
---

Rewrite the importer's retry rule for the team handbook. It used to say that failed batches are dropped after five retries; we reversed that last week, and now a failed batch goes to the dead-letter queue after five retries, where the on-call engineer replays it within a day. Print only the new rule, as the handbook should read today.
