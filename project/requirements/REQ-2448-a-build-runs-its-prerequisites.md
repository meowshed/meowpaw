---
id: REQ-2448
artifact: requirement
topic: packs
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0108
verification: behavioural
---

# REQ-2448

Where a build step has a prerequisite that another form of the same step
performs implicitly, the pack MUST perform it explicitly.

Otherwise a clean checkout fails in a way that reads as a defect in the
project rather than a missing step nobody wrote down.
