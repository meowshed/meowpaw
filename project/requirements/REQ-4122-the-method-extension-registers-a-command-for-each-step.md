---
id: REQ-4122
artifact: requirement
topic: pi-packages
class: functional
status: withdrawn
revised: 2026-10-31
verification: behavioural
elaborates: RES-0340
---

# REQ-4122

**Withdrawn. Replaced by REQ-3666.**

It read: the meow-flow extension registers a Pi command for each method step
(`research`, `requirements`, `design`, `spec`, `epic`, `implement`, `review`)
and for the driver (`run`), the initialiser (`init`) and the onboarding
command (`onboard`). Each command loads the corresponding skill and runs the
step. The command's description is the skill's description, so the model sees
the same routing information.

Withdrawn by ADR-3090.
