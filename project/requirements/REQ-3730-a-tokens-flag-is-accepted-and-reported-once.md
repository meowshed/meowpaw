---
id: REQ-3730
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

# REQ-3730

A start command that names `--tokens` MUST start the run with a notice that the bound no longer exists.

A command typed from habit is not refused over a bound that is not enforced, and the notice is withdrawn in the release after the one that adds it (RES-0351, conclusion 4).
