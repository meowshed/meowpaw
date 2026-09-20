---
id: REQ-2724
artifact: requirement
topic: safety
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0203
verification: behavioural
---

# REQ-2724

A hook MUST NOT log its input.

It inherits the session's environment and its input may contain material this
method forbids reading.
