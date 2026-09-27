---
id: REQ-0750
artifact: requirement
topic: state
class: functional
status: withdrawn
revised: 2026-09-27
elaborates: RES-0031, RES-0001
verification: static
---

# REQ-0750

**Withdrawn. Replaced by REQ-3072.**

It read: run state that is not worth a diff, such as the current step, the
pending approval, the recorded evidence and the revision counter, MUST live
outside the repository.

It counted recorded evidence as run state, which REQ-2956 keeps in the
repository, because RES-0262 found that evidence living on one machine is an
assertion. The owner chose the repository on 2026-09-27, so REQ-3072 keeps the
rest and leaves evidence out.
