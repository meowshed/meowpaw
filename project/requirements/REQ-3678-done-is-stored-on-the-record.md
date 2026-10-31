---
id: REQ-3678
artifact: requirement
topic: the-short-chain
class: functional
status: approved
revised: 2026-10-31
elaborates: RES-0369
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3678

A decision or defect whose work is complete MUST store `status: done`, set by one command in the pull request that completes it.

The merge is what closes it, and a status set later leaves a window in which the record lies.
