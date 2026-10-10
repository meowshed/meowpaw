---
id: REQ-4506
artifact: requirement
topic: shared-binary
class: functional
status: approved
revised: 2026-10-10
elaborates: RES-0347
verification: static
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-4506

A unit whose launcher finds no shared binary MUST report each of its checks as
unresolved, naming the core unit as what would supply it.
