---
id: REQ-2548
artifact: requirement
topic: source-control
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0132
verification: behavioural
---

# REQ-2548

Where the source-control tool in use cannot perform something the repository
depends on, the harness MUST report the capability as absent.

Attribute files that have no effect, annotated tags that cannot be made and
therefore cannot be signed, and configuration that is inert are each a process
the repository believes it has and does not.
