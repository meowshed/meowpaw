---
id: REQ-0878
artifact: requirement
topic: long-runs
class: functional
status: withdrawn
revised: 2026-10-10
elaborates: RES-0024, RES-0059
verification: behavioural
---

# REQ-0878

**Withdrawn by ADR-2910. Replaced by REQ-3724.**

It read: the budget MUST be checked before the next call rather than after it.

It held while a run had a token budget. With the token bound gone (ADR-2910) there is no budget to check, and the iteration ceiling and the time limit are checked after each turn, before the next iteration begins.
