---
id: REQ-2498
artifact: requirement
topic: runners
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0125
verification: behavioural
---

# REQ-2498

The harness MUST NOT attribute interleaved output or a summarising exit status
to one task where the run was parallel without output synchronisation or
continued past its first failure.
