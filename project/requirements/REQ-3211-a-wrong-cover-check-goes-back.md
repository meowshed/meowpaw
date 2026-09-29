---
id: REQ-3211
artifact: requirement
topic: the-method
class: functional
status: withdrawn
revised: 2026-09-29
elaborates: RES-0075
verification: behavioural
---

# REQ-3211

**Withdrawn by ADR-2300. Replaced by REQ-3644.**

It read: a check the implementation shows to be wrong MUST go back to the cover step, with the reason recorded in the task.

The step that wrote the check is the one that can change it without the change
reading as cheating.

ADR-2300 folds the cover step into implement: a task's tests are written first, in its own pull request, by the same context that implements it, and REQ-3644 states what holds in its place.
