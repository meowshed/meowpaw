---
id: REQ-0525
artifact: requirement
topic: artifacts
class: non-functional
status: approved
revised: 2026-09-20
elaborates: RES-0012, RES-0259
verification: static
---

# REQ-0525

The specification's index MUST be ordered so that a document appears after
everything it cites, so that reading it in order never requires a forward
reference.

The ordering carries the layering rule, and a violation is visible by reading
two identifiers. It does not generalise to an index over a record, which
REQ-2870 orders by identifier.
