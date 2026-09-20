---
id: REQ-1600
artifact: requirement
topic: memory
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0026
verification: behavioural
---

# REQ-1600

The harness MUST search its own record before generating a solution rather
than after, because after is a consistency check and before is what changes
the answer.
