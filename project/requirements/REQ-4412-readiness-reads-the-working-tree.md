---
id: REQ-4412
artifact: requirement
topic: source-control
class: functional
status: approved
revised: 2026-10-10
elaborates: RES-0346
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-4412

`paw ready implement` MUST read a task's approval from the working tree.

A task approved on the epic's own branch is ready, and the trunk no longer
decides whether it is.
