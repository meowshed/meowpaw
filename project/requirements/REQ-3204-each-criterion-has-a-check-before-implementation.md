---
id: REQ-3204
artifact: requirement
topic: the-method
class: functional
status: withdrawn
revised: 2026-09-29
elaborates: RES-0075
verification: behavioural
---

# REQ-3204

**Withdrawn by ADR-2300. Replaced by REQ-3640.**

It read: before any of a task's implementation exists, the cover step MUST write, for each acceptance criterion a program can check, at least one check that names that criterion.

A criterion without a check before the work starts is one the implementation
defines for itself.

ADR-2300 folds the cover step into implement: a task's tests are written first, in its own pull request, by the same context that implements it, and REQ-3640 states what holds in its place.
