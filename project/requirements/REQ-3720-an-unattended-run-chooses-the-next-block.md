---
id: REQ-3720
artifact: requirement
topic: unattended-runs
class: functional
status: approved
revised: 2026-10-03
elaborates: RES-0074
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3720

Where `paw status` has no line beginning `next:` and requirements are named by no task, an unattended run MUST choose the next block of them itself, marking the choice as a harness decision in its report.

The owner chose on 2026-10-03 that the run doesn't wait for a person to pick a topic. A block is one topic with neighbouring identifiers. It skips a postponed requirement and a requirement an approved decision already addresses. Where a requirement contradicts a record in force, the run writes the decision that amends that record and builds on it, because the owner said a newer decision is meant to change behaviour, and a run that leaves the contradiction for a person waits for someone who isn't there.
