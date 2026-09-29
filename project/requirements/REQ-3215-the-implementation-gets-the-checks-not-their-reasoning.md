---
id: REQ-3215
artifact: requirement
topic: the-method
class: functional
status: withdrawn
revised: 2026-09-29
elaborates: RES-0075
verification: evaluation
---

# REQ-3215

**Withdrawn by ADR-2300.**

It read: the implementing context MUST NOT be given the cover step's reasoning, only its checks and the task.

A model that reads why the checks were written implements to that reasoning
rather than to the criteria.

ADR-2300 folds the cover step into implement: a task's tests are written first, in its own pull request, by the same context that implements it, so this rule binds a step that no longer exists.
