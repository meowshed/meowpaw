---
id: REQ-3174
artifact: requirement
topic: routing
class: functional
status: approved
revised: 2026-09-21
unit: U-0001
elaborates: RES-0053
verification: judgement
---

# REQ-3174

A defect MUST carry a record of its own, unless a gate caught it and the same
change closed it.

A defect the gate caught leaves its evidence in the check that failed and the
commit that fixed it, and a record would add a file carrying no reasoning.
Every other defect is found by a person, routed somewhere, or reveals
something missing, and that reasoning outlives the change while the diff does
not.
