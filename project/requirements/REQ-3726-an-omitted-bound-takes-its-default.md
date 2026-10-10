---
id: REQ-3726
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

# REQ-3726

A start command that omits the iteration ceiling or the time limit MUST run with that bound's default.

A person who types the bare command still gets a run held to a ceiling and a limit, rather than a refusal or a run with none (RES-0351, conclusion 2).
