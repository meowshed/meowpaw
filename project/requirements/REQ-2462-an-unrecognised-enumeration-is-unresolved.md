---
id: REQ-2462
artifact: requirement
topic: runners
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0121, RES-0124
verification: behavioural
---

# REQ-2462

The harness MUST parse a runner's enumeration defensively and MUST report an
unrecognised shape as unresolved rather than as an empty task list.

None of these formats carries a stability promise and one disclaims it, and an
empty list reads as a repository that declares nothing.
