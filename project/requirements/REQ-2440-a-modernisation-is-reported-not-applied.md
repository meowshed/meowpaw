---
id: REQ-2440
artifact: requirement
topic: packs
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0102
verification: behavioural
---

# REQ-2440

A suggestion that code could use a newer feature MUST be reported rather than
applied during a check.

It is a fifth kind of finding - not a defect, a style preference, a
vulnerability or a type error - and a check that rewrites files is doing
something a check must not.
