---
id: REQ-3210
artifact: requirement
topic: the-method
class: functional
status: withdrawn
revised: 2026-09-29
elaborates: RES-0075
verification: behavioural
---

# REQ-3210

**Withdrawn by ADR-2300. Replaced by REQ-3644.**

It read: the implement step MUST NOT modify, delete, skip or weaken a check the cover step wrote.

An implementing agent that edits a failing check is indistinguishable from one
cheating it, which is how agents most often pass tests they can't satisfy.

ADR-2300 folds the cover step into implement: a task's tests are written first, in its own pull request, by the same context that implements it, and REQ-3644 states what holds in its place.
