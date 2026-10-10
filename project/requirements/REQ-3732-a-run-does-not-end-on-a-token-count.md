---
id: REQ-3732
artifact: requirement
topic: long-runs
class: functional
status: approved
revised: 2026-10-10
elaborates: RES-0351
source: the repository owner's decision
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3732

A run MUST NOT end because of a count of tokens.

The total a hook can make from the transcript counts each cache read again and
begins with the session and not with the run, so it ended a run in its first
iteration at 24.7 million against a stated 10 million (RES-0351, conclusion 1).
