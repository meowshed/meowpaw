---
id: REQ-0880
artifact: requirement
topic: long-runs
class: functional
status: withdrawn
revised: 2026-10-03
elaborates: RES-0024, RES-0059
source: the repository owner's decision
verification: behavioural
---

# REQ-0880

**Withdrawn by ADR-2380. Replaced by REQ-3702.**

It read: each iteration MUST begin from the same stated context.

It held while every iteration was a fresh `claude -p` session. The owner chose
to run the loop inside one session, where the conversation grows and
compaction summarises it, so no iteration starts from the same context
(RES-0320, conclusion 5). REQ-3702 keeps what a program can still give every
iteration: the same frozen prompt and the path of the progress file.
