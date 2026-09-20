---
id: REQ-2716
artifact: requirement
topic: safety
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0203
verification: behavioural
---

# REQ-2716

A hook that blocks MUST do a constant, small amount of work, and an expensive
check MUST run elsewhere with the hook denying by default.

A hook that times out does not block and the call proceeds, so enforcement
fails open exactly when the machine is slow.
