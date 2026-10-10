---
id: REQ-4414
artifact: requirement
topic: source-control
class: functional
status: approved
revised: 2026-10-10
elaborates: RES-0346
verification: judgement
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-4414

Where a person asks for the work of an epic whose records are approved on the
trunk, the method skill MUST implement its tasks on one branch and stop once, at
the pull request.

The merge of that pull request closes the epic, and no task of it needs a pull
request of its own.
