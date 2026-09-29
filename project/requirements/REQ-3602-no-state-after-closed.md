---
id: REQ-3602
artifact: requirement
topic: the-short-chain
class: functional
status: approved
revised: 2026-09-29
elaborates: RES-0310
verification: static
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3602

The record MUST NOT store or derive any state of a requirement after closed.

A verified state written after closing stalled the flow, and the gate that closes a task already runs the checks (RES-0310, conclusions 1 and 3).
