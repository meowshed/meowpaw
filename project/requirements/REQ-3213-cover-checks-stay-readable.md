---
id: REQ-3213
artifact: requirement
topic: the-method
class: functional
status: withdrawn
revised: 2026-09-29
elaborates: RES-0075
verification: behavioural
---

# REQ-3213

**Withdrawn by ADR-2300.**

It read: the implementing context MUST be able to read the checks its cover step wrote.

Hiding them stopped cheating in the benchmark but also cut legitimate
performance, and read-only access kept it.

ADR-2300 folds the cover step into implement: a task's tests are written first, in its own pull request, by the same context that implements it, so this rule binds a step that no longer exists.
