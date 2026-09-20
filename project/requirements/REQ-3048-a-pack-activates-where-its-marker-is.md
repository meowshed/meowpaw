---
id: REQ-3048
artifact: requirement
topic: universality
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0267
verification: behavioural
---

# REQ-3048

A pack MUST activate where its marker is found rather than once per
repository.

A repository with four languages then loads four packs, each applying where it
matched; REQ-2682 is what keeps each one scoped to its paths.
