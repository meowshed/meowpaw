---
id: REQ-1140
artifact: requirement
topic: prompt-format
class: functional
status: withdrawn
revised: 2026-09-23
elaborates: RES-0270
verification: evaluation
---

# REQ-1140

**Withdrawn. Replaced by REQ-1144, REQ-1146, REQ-1148 and REQ-1150.**

It read: a unit that has to be in context before the model acts MUST be loaded
by a mechanism that does not depend on the model choosing to load it, and how
often it is in context when needed MUST be measured.

The mechanism ADR-1020 chose for it did not work. A `SessionStart` hook naming the
writing skill left Sonnet 5 writing without it, while a description stating
the obligation loaded it in 36 of 36 writing runs and 0 of 39 near misses, as
RES-0272 records. The measurement it asked for stays, in REQ-1150.
