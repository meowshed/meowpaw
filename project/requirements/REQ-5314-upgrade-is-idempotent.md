---
id: REQ-5314
artifact: requirement
topic: upgrade
class: functional
status: approved
revised: 2026-10-31
elaborates: RES-0369
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-5314

An upgrade run on a record already in the required form MUST change nothing and say so.

A run that stopped halfway is resumed by running it again.
