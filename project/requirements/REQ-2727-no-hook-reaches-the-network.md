---
id: REQ-2727
artifact: requirement
topic: safety
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0203
verification: static
---

# REQ-2727

A hook the harness installs MUST NOT reach the network.

It runs on every matching event, under the session's own credentials, where
nothing is waiting to notice what it sent.
