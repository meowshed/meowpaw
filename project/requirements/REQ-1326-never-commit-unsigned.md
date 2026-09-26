---
id: REQ-1326
artifact: requirement
topic: source-control
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0025
verification: behavioural
---

# REQ-1326

Where signing is configured and a commit cannot be signed, the harness MUST
report it and MUST NOT commit unsigned.

A commit that cannot be signed is one the push will reject, so producing it
converts a clear failure here into an obscure one there.
