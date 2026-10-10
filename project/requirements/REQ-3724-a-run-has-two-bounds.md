---
id: REQ-3724
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

# REQ-3724

A run MUST end when it reaches the iteration ceiling or the time limit.

Both are counted outside the model and mean the same on every session, where
the only total a hook can make of tokens from the transcript counts each cache
read again and grows with the turns a session has taken and not with the work a
run has done (RES-0351, conclusion 1).
