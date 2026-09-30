---
id: REQ-3660
artifact: requirement
topic: the-short-chain
class: functional
status: approved
revised: 2026-09-30
elaborates: RES-0311
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3660

A task whose record is absent from the trunk the repository declares MUST NOT be reported ready to implement.

An approved status on an unmerged branch is a status waiting on its merge, and a session that remembers nothing can't otherwise tell it from an approval (RES-0311, conclusion 4).
