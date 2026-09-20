---
id: REQ-2566
artifact: requirement
topic: the-forge
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0133, RES-0134
verification: behavioural
---

# REQ-2566

The harness MUST read the limit and reset signals on every response, and MUST
honour a stated wait exactly rather than retrying sooner.

Retrying before the stated time worsens the limit, and a loop with no person
in it can spend an hour's quota in minutes.
