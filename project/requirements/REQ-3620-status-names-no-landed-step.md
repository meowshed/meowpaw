---
id: REQ-3620
artifact: requirement
topic: the-short-chain
class: functional
status: approved
revised: 2026-09-29
elaborates: RES-0310
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3620

The chain's status MUST NOT name as next a step whose work has already landed.

`paw status` named the document step after its work had merged (RES-0310, conclusion 10).
