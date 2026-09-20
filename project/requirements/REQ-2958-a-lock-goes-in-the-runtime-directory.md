---
id: REQ-2958
artifact: requirement
topic: state
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0262
source: the XDG base directory specification
verification: behavioural
---

# REQ-2958

A lock or a socket MUST be placed in the platform's runtime directory, which
is user-owned and whose contents MUST NOT survive a restart.
