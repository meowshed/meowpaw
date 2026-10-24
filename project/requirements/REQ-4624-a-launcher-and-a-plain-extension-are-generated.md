---
id: REQ-4624
artifact: requirement
topic: pi-packages
class: functional
status: approved
revised: 2026-10-24
elaborates: RES-0354
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-4624

A unit's launcher, and a Pi extension that only puts that launcher on the path,
MUST be generated from one template by a program of this repository and never
written by hand for each unit.

A Pi extension that carries a host's hooks or commands is the one exception and
stays hand-written, because no template expresses what it adapts.
