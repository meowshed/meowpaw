---
id: REQ-1720
artifact: requirement
topic: quality-attributes
class: non-functional
status: approved
revised: 2026-09-20
elaborates: RES-0031
verification: behavioural
---

# REQ-1720

Every step MUST be idempotent: invoked twice with no intervening change, the
second invocation MUST produce the same artifact state and MUST say that
nothing moved.
