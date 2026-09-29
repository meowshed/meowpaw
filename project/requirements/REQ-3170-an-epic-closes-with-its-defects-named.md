---
id: REQ-3170
artifact: requirement
topic: keeping-artifacts-current
class: functional
status: withdrawn
revised: 2026-09-29
elaborates: RES-0055
verification: judgement
---

# REQ-3170

**Withdrawn by ADR-2300. Replaced by REQ-3610.**

It read: an epic MAY be closed while a defect it uncovered is open, provided the defect is recorded; where the defect contradicts one of the epic's acceptance criteria, the epic MUST name that criterion, name the defect, and state why closing is correct.

Without this an epic whose work is finished stays open for ever, or is reported
as realised while its own criterion fails, and the second is the unearned
answer the method exists to prevent. Naming the contradiction costs three
sentences and leaves a reader able to disagree.

ADR-2300 closes a requirement with the tasks that name it and keeps no verification step, evidence file or record review, and REQ-3610 states what holds in its place.
