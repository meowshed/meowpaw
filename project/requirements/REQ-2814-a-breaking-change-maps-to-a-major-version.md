---
id: REQ-2814
artifact: requirement
topic: source-control
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0221
source: semantic versioning
verification: behavioural
---

# REQ-2814

A commit marked as breaking an interface MUST map to a major version in the
release it lands in.

Marking it and then releasing it as a minor version is the same as not marking
it; REQ-2212 is what requires the mark.
