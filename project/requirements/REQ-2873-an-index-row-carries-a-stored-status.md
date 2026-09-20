---
id: REQ-2873
artifact: requirement
topic: artifacts
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0259
verification: static
---

# REQ-2873

An index row MUST carry only a stored status.

A derived one recomputed into a row is a second copy that is wrong whenever
the tree has moved and the row has not.
