---
id: REQ-3212
artifact: requirement
topic: the-method
class: functional
status: withdrawn
revised: 2026-09-29
elaborates: RES-0075
verification: behavioural
---

# REQ-3212

**Withdrawn by ADR-2300.**

It read: while a task is implemented, a program MUST refuse any change to the checks its cover step wrote.

A rule the implementing agent is told to follow holds only as long as it
complies, and read-only access stopped test modification in the benchmark.

ADR-2300 folds the cover step into implement: a task's tests are written first, in its own pull request, by the same context that implements it, so this rule binds a step that no longer exists.
