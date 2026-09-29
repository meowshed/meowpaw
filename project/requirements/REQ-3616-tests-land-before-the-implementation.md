---
id: REQ-3616
artifact: requirement
topic: the-short-chain
class: functional
status: approved
revised: 2026-09-29
elaborates: RES-0310
verification: judgement
verifier: person
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3616

A task's tests MUST land in the task's own pull request, in a commit before any commit that implements the task.

Writing the tests first is the whole of what the cover step did, and a pull request of its own for them only added a merge (RES-0310, conclusion 8; the owner's instruction).
