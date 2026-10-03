---
id: REQ-3752
artifact: requirement
topic: prose-and-comments
class: functional
status: approved
revised: 2026-10-03
elaborates: RES-0330
source: the repository owner's request, and BUG-1230
verification: evaluation
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3752

Before a release ships a judged rule, a run by hand MUST show the gate passing
each of BUG-1230's four texts in three runs of three, and blocking one text per
judged rule that breaks it in three runs of three, with no run in CI.

The four texts are the cases the gate failed on, and a run in CI would call a
model on every change, which the owner ruled out. Three runs show a false
block that is frequent, not one that is rare, so the result is a smoke check
and is reported as one.
