---
id: REQ-4706
artifact: requirement
topic: tracker-sync
class: functional
status: approved
revised: 2026-10-10
elaborates: RES-0349
verification: judgement
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-4706

The method MUST run a synchronisation at the start and at the end of an epic's
work, and a synchronisation MUST NOT run in the background.

The owner asked for it to be automatic, and a run no person starts is a run
without a gate, so the method is what makes it automatic.
