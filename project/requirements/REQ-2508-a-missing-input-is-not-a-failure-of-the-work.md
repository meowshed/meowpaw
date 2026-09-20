---
id: REQ-2508
artifact: requirement
topic: runners
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0123
verification: behavioural
---

# REQ-2508

Where a task declares inputs it requires, the harness MUST read them before
invoking it and MUST report a missing one as a missing input rather than as a
failure of the code.
