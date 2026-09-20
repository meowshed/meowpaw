---
id: REQ-0263
artifact: requirement
topic: the-method
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0055
verification: static
unit: U-0001
---

# REQ-0263

A task MUST be a vertical slice with behaviour someone can observe.

A task that produces nothing observable cannot be verified by anything except
reading its diff, which is how a cut that was wrong survives to the end.
