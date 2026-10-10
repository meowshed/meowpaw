---
id: REQ-1353
artifact: requirement
topic: the-forge
class: functional
status: withdrawn
revised: 2026-10-10
elaborates: RES-0025
verification: static
---

# REQ-1353

**Withdrawn. Replaced by REQ-4700 and REQ-4702.**

It read: writes MUST flow from the record to the tracker, with tracker state read back, and marking an item done MUST be the only write permitted in the other direction.

RES-0349 finds that which side changed can only be told from a fingerprint of
each side, so ADR-2890 changes what it says: the side that changed is applied, and the state still flows to the record.
