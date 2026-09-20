---
id: REQ-2848
artifact: requirement
topic: helpers
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0241
verification: behavioural
---

# REQ-2848

The harness MUST wait for a server that is starting rather than treat it as
absent.

Degrading immediately degrades every time on a large project, which is where
the server was worth having.
