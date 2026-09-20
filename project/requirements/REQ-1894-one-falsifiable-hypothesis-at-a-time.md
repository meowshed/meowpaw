---
id: REQ-1894
artifact: requirement
topic: debugging
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0015
verification: behavioural
unit: U-0001
---

# REQ-1894

The harness MUST hold one falsifiable hypothesis at a time and MUST test it by
trying to refute it.

Two hypotheses at once mean neither is tested: whichever is abandoned first is
abandoned for the wrong reason.
