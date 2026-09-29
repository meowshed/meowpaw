---
id: REQ-3606
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

# REQ-3606

A task MUST NOT be marked done in a change whose gate has not passed.

The gate is what settles the requirements a task closes, so a done mark without it closes them on nothing (RES-0310, conclusion 3).
