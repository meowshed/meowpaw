---
id: REQ-2728
artifact: requirement
topic: safety
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0203
verification: behavioural
---

# REQ-2728

The harness MUST advance its revision counter after a failed tool use as well
as a successful one, because a command that failed can still have changed the
tree.
