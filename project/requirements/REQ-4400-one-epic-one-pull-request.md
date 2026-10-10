---
id: REQ-4400
artifact: requirement
topic: source-control
class: functional
status: approved
revised: 2026-10-10
elaborates: RES-0346
verification: static
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-4400

The work of one epic that a person asks for MUST map to one branch, one pull
request and one review.

The work is the whole cycle from the epic's research, or the implementation of
an epic whose records are already approved on the trunk. Its tasks are groups
of commits on that branch, each with its tests first.
