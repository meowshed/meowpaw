---
id: REQ-2966
artifact: requirement
topic: state
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0262
verification: behavioural
---

# REQ-2966

State MUST be written atomically, through a temporary file renamed into place.

A concurrent reader then sees one version or the other rather than half of
each.
