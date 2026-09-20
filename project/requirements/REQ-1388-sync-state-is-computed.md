---
id: REQ-1388
artifact: requirement
topic: the-forge
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0025
verification: static
---

# REQ-1388

Synchronisation state MUST be computed by comparing the mapping's fingerprint
against the tracker rather than stored, because a stored derived state is a
second source of truth.
