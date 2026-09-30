---
id: REQ-3656
artifact: requirement
topic: the-short-chain
class: functional
status: approved
revised: 2026-09-30
elaborates: RES-0310
verification: static
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3656

Where a person asks for a decision to land in one pull request, the method MUST write each of its records as a draft, check it, set it to `approved` for the step after it, and stop once, at that pull request.

Without the request the method stops at every approval gate. A request for one pull request is no approval of what it will hold, so the stop moves to the pull request and doesn't go away: the status written there takes effect when the person merges it (RES-0310; the owner's instruction).
