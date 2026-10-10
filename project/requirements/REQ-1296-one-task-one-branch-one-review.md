---
id: REQ-1296
artifact: requirement
topic: source-control
class: functional
status: withdrawn
revised: 2026-10-10
elaborates: RES-0014, RES-0002
verification: static
---

# REQ-1296

**Withdrawn. Replaced by REQ-4400, REQ-4402 and REQ-4404.**

It read: one task MUST map to one branch, one pull request and one review.

An epic carries 2.7 tasks on average, so a pull request for each task, and a
stop at the records before the implementation, opened about four where one
carries the same commits (RES-0346). ADR-2860 moves the unit of a pull request
from the task to the epic and to the defect, and the stop to its merge.
