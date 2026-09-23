---
name: write-decision-note
description: A writing task where the standard's defects appear without the skill.
tags: [content]
runs: 5
max_turns: 6
---

Summarise for the team, as a short Markdown note, why we moved the importer's retries from a fixed two-second wait to exponential backoff with jitter. The upstream API started returning 429 under load, and the fixed wait kept every client retrying in lockstep. Print only the note.
