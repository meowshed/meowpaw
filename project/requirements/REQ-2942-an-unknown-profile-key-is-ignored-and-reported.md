---
id: REQ-2942
artifact: requirement
topic: routing
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0261
verification: behavioural
---

# REQ-2942

The harness MUST ignore a profile key it does not know and MUST report it.

That keeps an older harness working against a newer profile while telling the
user why their setting had no effect.
