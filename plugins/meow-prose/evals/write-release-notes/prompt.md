---
name: write-release-notes
description: A writing task where the standard's defects appear without the skill.
tags: [content]
runs: 5
max_turns: 6
---

Write release notes for version 2.3 of the importer. Changes: retries now back off exponentially; failed batches go to a dead-letter queue instead of being dropped; the CSV parser now accepts quoted commas; start-up is 40% faster because the schema is cached. Print only the notes.
