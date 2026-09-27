---
id: REQ-3072
artifact: requirement
topic: state
class: functional
status: approved
revised: 2026-09-27
elaborates: RES-0031, RES-0262
source: the repository owner's decision on 2026-09-27 that evidence stays in the repository, which left recorded evidence out of run state
verification: static
---

# REQ-3072

Run state, meaning what a second person on another machine doesn't need to
trust the work, such as the current step, the fact that an approval is
pending, the revision counter and the harness's log of what it did as distinct
from the output it found, MUST live outside the repository, because losing it
costs a resumption and never the project.
