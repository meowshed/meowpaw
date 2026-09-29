---
id: REQ-3642
artifact: requirement
topic: the-short-chain
class: functional
status: approved
revised: 2026-09-29
elaborates: RES-0310
verification: judgement
verifier: person
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3642

Each test written ahead of a task's implementation MUST fail at the commit that adds it.

A test that passed before the implementation existed tests nothing the task added, and the commit shows the failure without a kept run (RES-0310, conclusions 7 and 8).
