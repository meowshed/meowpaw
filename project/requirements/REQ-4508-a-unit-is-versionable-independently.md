---
id: REQ-4508
artifact: requirement
topic: shared-binary
class: functional
status: approved
revised: 2026-10-10
elaborates: RES-0347
verification: static
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-4508

Each unit MUST be versionable independently of every other one.

Installing and removing are no longer independent of the core unit (REQ-4502),
and the version still is: a unit releases on its own tag and its own number.
