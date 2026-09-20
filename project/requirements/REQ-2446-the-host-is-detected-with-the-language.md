---
id: REQ-2446
artifact: requirement
topic: packs
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0109, RES-0110
verification: behavioural
---

# REQ-2446

Where a language is evaluated by a host or has several implementations, the
pack MUST detect which one applies and MUST report every verb unresolved until
it has.

A command from the wrong implementation frequently succeeds and does something
else, so a zero exit from an unidentified one is not evidence.
