---
name: write-explanation
description: A writing task where the standard's defects appear without the skill.
tags: [content]
runs: 5
max_turns: 6
---

Explain to a new engineer, in about 300 words, how the importer decides whether a batch is valid: it checks the schema version, rejects rows with missing required fields, and quarantines the batch if more than 5% of rows fail rather than dropping them. Print only the explanation.
