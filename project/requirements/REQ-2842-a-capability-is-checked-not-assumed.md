---
id: REQ-2842
artifact: requirement
topic: helpers
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0241
verification: behavioural
---

# REQ-2842

The harness MUST check that a server supports a feature before using it, and
MUST read the announced capabilities defensively.

The protocol states that not every server supports every feature and allows
properties the reader does not know about.
