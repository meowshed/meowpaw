---
id: REQ-0210
artifact: requirement
topic: the-method
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0064
verification: behavioural
---

# REQ-0210

The command that drives the chain MUST be idempotent when invoked again with
no approval in between, and MUST say that it is waiting rather than repeating
the step.
