---
id: REQ-3201
artifact: requirement
topic: the-method
class: functional
status: approved
revised: 2026-09-27
elaborates: RES-0001
verification: static
---

# REQ-3201

Each step of the method MUST leave its artifact as a file committed to the
repository.

A step whose output lives only in a session can't be approved, cited or
checked by the step after it.
