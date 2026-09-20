---
id: REQ-2422
artifact: requirement
topic: packs
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0101, RES-0104
verification: behavioural
---

# REQ-2422

A pack MUST NOT enable a lint group, a strictness setting or an analysis level
the repository did not ask for.

The findings that result are style preferences the reader cannot tell from
defects, and in a compiled language they block the build rather than the lint.
