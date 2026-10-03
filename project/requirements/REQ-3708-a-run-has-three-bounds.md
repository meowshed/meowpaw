---
id: REQ-3708
artifact: requirement
topic: long-runs
class: functional
status: approved
revised: 2026-10-03
elaborates: RES-0320, RES-0074
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3708

A run MUST end when it reaches the iteration ceiling, the time limit or the token budget the person stated in its start command, which requires all three.

A run on the whole chain can stay busy for days, so each bound stops a different way of spinning: the count stops many small iterations, the time stops slow ones, and the tokens stop expensive ones. A hook can count tokens from the transcript, and no field gives it the spend in dollars (RES-0320, conclusion 10).
