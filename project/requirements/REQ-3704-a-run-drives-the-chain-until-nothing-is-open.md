---
id: REQ-3704
artifact: requirement
topic: long-runs
class: functional
status: approved
revised: 2026-10-03
elaborates: RES-0320, RES-0074
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3704

A run MUST repeat iterations of `/meow-flow:run` until `paw status` reports no requirement open and no defect open, where a postponed requirement doesn't count as open.

The owner chose on 2026-10-03 that one run carries the whole chain, so the run ends when the record holds no more work. A postponed requirement waits on the condition its decision states, so counting it would keep a run going on work nobody may start. Replaces REQ-0888.
