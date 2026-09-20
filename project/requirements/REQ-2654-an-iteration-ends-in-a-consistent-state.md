---
id: REQ-2654
artifact: requirement
topic: long-runs
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0155
verification: behavioural
---

# REQ-2654

Each iteration of a long run MUST end in a recorded, consistent state.

That boundary is the only place where stopping costs nothing, so it decides
whether the run can be stopped at all.
