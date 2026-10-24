---
id: REQ-3273
artifact: requirement
topic: delegation
class: functional
status: approved
revised: 2026-10-24
elaborates: RES-0368
verification: static
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3273

A page that ships an agent MUST state which name reaches the unit's definition
and which name reaches a repository's own agent of the same name.

A reader who defines an agent of the same name expecting it to replace the
unit's gets the unit's, because the platform keeps both.
