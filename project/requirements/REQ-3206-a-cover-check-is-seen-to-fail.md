---
id: REQ-3206
artifact: requirement
topic: the-method
class: functional
status: withdrawn
revised: 2026-09-29
elaborates: RES-0075
verification: behavioural
---

# REQ-3206

**Withdrawn by ADR-2300. Replaced by REQ-3642.**

It read: each check the cover step writes MUST be seen to fail against the tree before the implementation starts.

A check that passes before the work exists can't show that the work did
anything.

ADR-2300 folds the cover step into implement: a task's tests are written first, in its own pull request, by the same context that implements it, and REQ-3642 states what holds in its place.
