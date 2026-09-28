---
id: REQ-3213
artifact: requirement
topic: the-method
class: functional
status: approved
revised: 2026-09-27
elaborates: RES-0075
verification: behavioural
---

# REQ-3213

The implementing context MUST be able to read the checks its cover step
wrote.

Hiding them stopped cheating in the benchmark but also cut legitimate
performance, and read-only access kept it.
