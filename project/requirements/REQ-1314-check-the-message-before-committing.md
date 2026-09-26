---
id: REQ-1314
artifact: requirement
topic: source-control
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0025
verification: behavioural
---

# REQ-1314

The harness MUST check its own message against the convention and its declared
trailers before committing, and MUST report a violation rather than
committing.

The platform has no rule that matches a message, so nothing downstream catches
this one.
