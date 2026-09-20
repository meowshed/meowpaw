---
id: REQ-0514
artifact: requirement
topic: artifacts
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0012
verification: static
---

# REQ-0514

Each artifact MUST carry machine-readable metadata, in the document itself,
declaring its kind, its status and the date it was last revised.

Staleness is then visible without reading the document, and a tool that has to
infer a kind from a path is a tool that is wrong after the first
reorganisation.
