---
id: REQ-4804
artifact: requirement
topic: reviewer-coverage
class: functional
status: approved
revised: 2026-10-10
elaborates: RES-0350
source: BUG-1100
verification: static
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-4804

The reviewer's labelled set MUST list each rule of the writing standard that no
text can show, with the reason for each.

A rule dropped from the list shows in the diff, and one silently skipped
doesn't, so the list keeps the check of REQ-4802 strict where a rule describes
the review or the writer's process.
