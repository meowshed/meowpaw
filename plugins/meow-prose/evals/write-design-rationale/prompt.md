---
name: write-design-rationale
description: A writing task where the standard's patterns appear without the skill.
tags: [content, patterns]
runs: 5
max_turns: 6
---

Explain to the platform team, in about 200 words, why we chose PostgreSQL's LISTEN/NOTIFY over Kafka for the importer's job queue. Facts: one team runs it; the queue peaks at 40 jobs a minute; Kafka would need a three-broker cluster nobody here operates; LISTEN/NOTIFY drops messages when no listener is connected, so the worker polls a jobs table on start-up to catch up. Print only the text.
