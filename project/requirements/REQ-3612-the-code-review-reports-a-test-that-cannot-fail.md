---
id: REQ-3612
artifact: requirement
topic: the-short-chain
class: functional
status: approved
revised: 2026-09-29
elaborates: RES-0310
verification: judgement
verifier: agent
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3612

The code review of a task MUST report each test in the change that would still pass against a wrong implementation.

Each of the four unmet requirements RES-0309 found had such a test, and with verification gone the code review is the one reader left that sees the test beside the code (RES-0310, conclusion 6).
