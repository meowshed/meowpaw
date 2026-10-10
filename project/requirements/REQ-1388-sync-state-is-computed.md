---
id: REQ-1388
artifact: requirement
topic: the-forge
class: functional
status: withdrawn
revised: 2026-10-10
elaborates: RES-0025
verification: static
---

# REQ-1388

**Withdrawn. Replaced by REQ-4704.**

It read: synchronisation state MUST be computed by comparing the mapping's fingerprint against the tracker rather than stored, because a stored derived state is a second source of truth.

RES-0349 finds that which side changed can only be told from a fingerprint of
each side, so ADR-2890 changes what it says: the tracker side's fingerprint is stored beside the record side's.
