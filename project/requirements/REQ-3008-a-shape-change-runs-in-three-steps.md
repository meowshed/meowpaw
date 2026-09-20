---
id: REQ-3008
artifact: requirement
topic: keeping-artifacts-current
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0265
verification: behavioural
---

# REQ-3008

A change to the record's shape MUST run as expand, migrate and contract.

An unfinished migration is worse than none, because every check, reader and
generator then has to know both forms forever.
