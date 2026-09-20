---
id: REQ-1355
artifact: requirement
topic: the-forge
class: non-functional
status: approved
revised: 2026-09-20
elaborates: RES-0025
verification: behavioural
unit: U-0001
---

# REQ-1355

Synchronisation MUST be deterministic and idempotent.

A synchronisation that is neither is a synchronisation nobody dares replay,
which is the moment it is most needed; REQ-0466 is what requires its failure
paths to be checked.
