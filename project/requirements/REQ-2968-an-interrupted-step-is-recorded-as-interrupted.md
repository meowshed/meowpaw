---
id: REQ-2968
artifact: requirement
topic: state
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0262
verification: behavioural
---

# REQ-2968

A step MUST be recorded as started before it runs, and MUST be reported as
interrupted on resume rather than silently retried.

Retrying repeats side effects that may already have happened.
