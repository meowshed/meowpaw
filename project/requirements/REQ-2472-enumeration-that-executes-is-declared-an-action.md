---
id: REQ-2472
artifact: requirement
topic: runners
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0125, RES-0121
verification: behavioural
---

# REQ-2472

Where enumerating a runner's tasks can execute the repository's code, the
harness MUST prefer a static read for detection.

This was verified rather than assumed: make updates the makefiles it reads,
and neither dry run nor question mode prevents it.
