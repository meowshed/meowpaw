---
id: REQ-0750
artifact: requirement
topic: state
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0031, RES-0001
verification: static
---

# REQ-0750

Run state that is not worth a diff, such as the current step, the pending
approval, the recorded evidence and the revision counter, MUST live outside
the repository.
