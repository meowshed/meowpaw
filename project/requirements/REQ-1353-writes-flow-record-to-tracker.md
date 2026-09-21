---
id: REQ-1353
artifact: requirement
topic: the-forge
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0025
verification: static
---

# REQ-1353

Writes MUST flow from the record to the tracker, with tracker state read back,
and marking an item done MUST be the only write permitted in the other
direction.

That is the one thing people do in the tracker rather than in the repository.
