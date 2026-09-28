---
id: REQ-1362
artifact: requirement
topic: the-forge
class: functional
status: withdrawn
revised: 2026-09-28
elaborates: RES-0022
verification: static
---

# REQ-1362

**Withdrawn by ADR-1800. Replaced by REQ-3320.**

It read: the epic MUST be the only grouping the harness keeps above a task. Its
reason, from RES-0022, was that a grouping the tracker keeps and the record
doesn't is a second plan.

REQ-0354 lets a defect carry its own tasks, so a task realising a one-task fix sits under its defect and under no
epic. No design could meet both, so REQ-3320 names the two records a task may
sit under and keeps the rest of the obligation: nothing else groups tasks, in
the record or on a tracker.
