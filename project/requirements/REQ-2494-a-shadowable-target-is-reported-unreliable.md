---
id: REQ-2494
artifact: requirement
topic: runners
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0125
verification: behavioural
---

# REQ-2494

Where a runner's task can be shadowed by a file of the same name, the harness
MUST report a task that is not protected against it as unreliable.

It stops running the moment a file of that name exists, which is usually the
first time it succeeds.
