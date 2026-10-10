---
id: REQ-3662
artifact: requirement
topic: the-short-chain
class: functional
status: withdrawn
revised: 2026-10-10
elaborates: RES-0311
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3662

**Withdrawn. Replaced by REQ-4412.**

It read: `paw status` MUST name a task waiting on its merge in place of `next: implement`.

An epic carries 2.7 tasks on average, so a pull request for each task, and a
stop at the records before the implementation, opened about four where one
carries the same commits (RES-0346). ADR-2860 moves the unit of a pull request
from the task to the epic and to the defect, and the stop to its merge.
