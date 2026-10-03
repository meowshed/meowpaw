---
id: REQ-3710
artifact: requirement
topic: long-runs
class: functional
status: approved
revised: 2026-10-03
elaborates: RES-0320, RES-0074
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3710

A run MUST end as stuck, naming the counts, after two iterations in a row in which the tree is unchanged and no count of open requirements or open defects fell.

A run that retries forever on work it can't do spends its budget and tells nobody, so it stops with the counts that didn't move. Two iterations, as REQ-0886 states, because one iteration can rightly only read.
