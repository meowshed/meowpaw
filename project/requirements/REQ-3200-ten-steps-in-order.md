---
id: REQ-3200
artifact: requirement
topic: the-method
class: functional
status: approved
revised: 2026-09-27
elaborates: RES-0001, RES-0075
verification: static
---

# REQ-3200

The method MUST proceed through ten named steps in this order: research,
requirements, design, spec, epic, cover, implement, document, verify, review.

Each step reads what the one before it approved, so the order is what keeps a
step from building on a decision nobody made. The cover step sits between the
epic and the implementation because tests written after faulty code catch
about half the faults that tests written independently do.
