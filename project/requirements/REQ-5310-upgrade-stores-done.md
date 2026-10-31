---
id: REQ-5310
artifact: requirement
topic: upgrade
class: functional
status: approved
revised: 2026-10-31
elaborates: RES-0369
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-5310

The upgrade MUST store `done` on each decision and defect the old marks derive as complete.

Once the marks are archived, nothing can compute that state again.
