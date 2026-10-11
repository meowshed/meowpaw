---
id: REQ-4800
artifact: requirement
topic: reviewer-coverage
class: functional
status: withdrawn
revised: 2026-10-11
elaborates: RES-0350
source: BUG-1100
verification: static
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-4800

The reviewer's labelled set MUST hold at least one case for every rule of the writing standard that a reader can see broken in a text.
**Withdrawn by ADR-2980 on 2026-10-11. No replacement.**

It made the measurement of a prompt obligatory, and ADR-2980 removed prompt
evaluation whole, because the owner will redesign it in future.

A rate measured on some of the rules reads as a rate for all of them, so a rule with no case is a rule whose review has never been measured, and the published rate says nothing about it.
