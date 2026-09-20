---
id: REQ-2468
artifact: requirement
topic: runners
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0121, RES-0122, RES-0123
verification: behavioural
---

# REQ-2468

Where a runner skips a task as fresh or as already satisfied, the harness MUST
report it as skipped, MUST NOT report it as passed, and MUST NOT cite it as
evidence.

The run did not happen, so there is nothing it can be evidence of.
