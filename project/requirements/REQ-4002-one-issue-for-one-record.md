---
id: REQ-4002
artifact: requirement
topic: tracker
class: functional
status: approved
revised: 2026-10-31
elaborates: RES-0369
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-4002

Where a repository declares a tracker, the harness MUST be able to project each approved decision or defect onto one issue, recording the issue and a fingerprint of what it wrote on the decision or defect.

The record stays the source of truth for the work, the tracker for what is happening to it, and a replay finds nothing to do.
