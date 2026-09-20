---
id: REQ-2432
artifact: requirement
topic: packs
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0103, RES-0105
verification: behavioural
---

# REQ-2432

A pack MUST report which rule groups or analyses were enabled when it reports
a verb as clean.

A clean result under a default configuration is a statement about the
configuration rather than about the code, and reporting it as the second is
how a security rule that was never on gets counted as passing.
