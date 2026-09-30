---
id: REQ-3664
artifact: requirement
topic: the-short-chain
class: functional
status: approved
revised: 2026-09-30
elaborates: RES-0311
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3664

Where the repository declares no trunk, or the trunk can't be read, the record program MUST say that an approval can't be told from one waiting on a merge.

Refusing every task there would stop a repository with no code host, and passing in silence would hide that the guard is absent (RES-0311, conclusion 6).
