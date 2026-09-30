---
id: REQ-3656
artifact: requirement
topic: the-short-chain
class: functional
status: approved
revised: 2026-09-30
elaborates: RES-0311
verification: static
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3656

Where a person asks for a decision to land in one pull request, the method MUST stop once, at that pull request.

The merge of that pull request is the approval, so a stop at each gate before it asks for the same approval several times. Without the request, every gate stops (RES-0311, conclusions 1 and 2).
