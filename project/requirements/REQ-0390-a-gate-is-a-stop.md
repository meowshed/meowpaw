---
id: REQ-0390
artifact: requirement
topic: gates-and-approval
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0031, RES-0001, RES-0002
verification: behavioural
---

# REQ-0390

Where a step's output requires approval, the harness MUST stop after producing
it and MUST NOT continue on its own answer.

**Amended by ADR-2310.** Where a person asks for a decision to land in one
pull request, the one stop is at that pull request, as REQ-3656 states.
