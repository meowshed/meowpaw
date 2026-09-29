---
id: REQ-3648
artifact: requirement
topic: the-short-chain
class: functional
status: approved
revised: 2026-09-29
elaborates: RES-0310
verification: static
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3648

The record MUST accept a task or an epic that names any number of requirements, and a requirement named by any number of tasks and epics.

A requirement often needs a program change and a prompt change, and one task often settles several requirements, so a one-to-one rule forces either a split nobody reviews or a false coverage finding (the owner's instruction).
