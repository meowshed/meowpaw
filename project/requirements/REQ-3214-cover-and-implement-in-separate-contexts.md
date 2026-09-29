---
id: REQ-3214
artifact: requirement
topic: the-method
class: functional
status: withdrawn
revised: 2026-09-29
elaborates: RES-0075
verification: evaluation
---

# REQ-3214

**Withdrawn by ADR-2300.**

It read: the cover step MUST run in a context separate from the one that implements the task.

The platform's own guidance has one context write the tests and another the
code, so that neither is written from the other's reasoning.

ADR-2300 folds the cover step into implement: a task's tests are written first, in its own pull request, by the same context that implements it, so this rule binds a step that no longer exists.
