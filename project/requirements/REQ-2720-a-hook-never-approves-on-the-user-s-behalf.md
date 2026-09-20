---
id: REQ-2720
artifact: requirement
topic: safety
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0203
verification: behavioural
---

# REQ-2720

A hook the harness ships MUST NOT answer that a call is allowed, because that
skips the permission flow for whatever matched, which is the repository's
decision.
