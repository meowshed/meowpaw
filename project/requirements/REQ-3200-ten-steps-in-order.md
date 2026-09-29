---
id: REQ-3200
artifact: requirement
topic: the-method
class: functional
status: withdrawn
revised: 2026-09-29
elaborates: RES-0001, RES-0075
verification: static
---

# REQ-3200

**Withdrawn by ADR-2300. Replaced by REQ-3638.**

It read: the method MUST proceed through ten named steps in this order: research, requirements, design, spec, epic, cover, implement, document, verify, review.

Each step reads what the one before it approved, so the order is what keeps a
step from building on a decision nobody made. The cover step sits between the
epic and the implementation because tests written after faulty code catch
about half the faults that tests written independently do.

ADR-2300 closes a requirement with the tasks that name it and keeps no verification step, evidence file or record review, and REQ-3638 states what holds in its place.
