---
id: REQ-2484
artifact: requirement
topic: runners
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0121
verification: behavioural
---

# REQ-2484

Scripts declared in a package manager's manifest MUST be read by the language
pack that owns the manifest and MUST NOT also be read as a runner's tasks.

One file with two readers produces two answers for the same verb and no rule
for which wins.
