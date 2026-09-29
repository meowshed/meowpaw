---
id: REQ-3208
artifact: requirement
topic: the-method
class: functional
status: withdrawn
revised: 2026-09-29
elaborates: RES-0075
verification: behavioural
---

# REQ-3208

**Withdrawn by ADR-2300. Replaced by REQ-3616.**

It read: the checks the cover step writes MUST land in a commit of their own, before any commit that implements the task.

A reviewer then reads what the task must pass apart from what makes it pass.

ADR-2300 folds the cover step into implement: a task's tests are written first, in its own pull request, by the same context that implements it, and REQ-3616 states what holds in its place.
