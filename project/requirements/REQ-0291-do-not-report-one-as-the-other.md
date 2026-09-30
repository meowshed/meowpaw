---
id: REQ-0291
artifact: requirement
topic: the-method
class: functional
status: withdrawn
revised: 2026-09-30
elaborates: RES-0063, RES-0067
verification: behavioural
---

# REQ-0291

**Withdrawn by ADR-2300.**

It read: a failure in checking the record MUST NOT be reported as a failure of the task that happened to be in flight, and a task that fails verification MUST NOT be reported as a defect in the record.

ADR-2300 removes the verification step this rule kept apart from checking the record.
