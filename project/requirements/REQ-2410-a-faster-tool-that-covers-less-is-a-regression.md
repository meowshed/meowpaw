---
id: REQ-2410
artifact: requirement
topic: packs
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0101, RES-0106
verification: behavioural
---

# REQ-2410

Where a pack resolves a verb to a tool that covers less than the ecosystem's
default, it MUST run the remainder as well or report what is no longer
checked.

A substitution that is faster and narrower reports success while a whole
category stops being checked, and nothing in the result says so.
