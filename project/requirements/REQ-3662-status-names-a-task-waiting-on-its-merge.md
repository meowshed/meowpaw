---
id: REQ-3662
artifact: requirement
topic: the-short-chain
class: functional
status: approved
revised: 2026-09-30
elaborates: RES-0311
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3662

The chain's status MUST report a task whose record is absent from the declared trunk as waiting on its merge.

A driver reads only the status, so a task named next is a task it starts (RES-0311, conclusion 5).
