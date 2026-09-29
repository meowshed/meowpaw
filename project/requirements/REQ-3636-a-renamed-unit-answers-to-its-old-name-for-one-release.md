---
id: REQ-3636
artifact: requirement
topic: the-short-chain
class: functional
status: approved
revised: 2026-09-29
elaborates: RES-0310
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3636

When a unit is renamed, installing or running it under its old name MUST keep working for one release and say it is deprecated.

The harness renamed `meow-method` this way, and a rename that breaks at once strands every repository still naming the old unit (RES-0310, conclusion 18).
