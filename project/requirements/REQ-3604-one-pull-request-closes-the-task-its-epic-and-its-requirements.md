---
id: REQ-3604
artifact: requirement
topic: the-short-chain
class: functional
status: approved
revised: 2026-09-29
elaborates: RES-0310
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3604

When a task's pull request merges, the task, its epic where the task was the epic's last open one, and each requirement that no open task or epic still names MUST be closed by that merge, with no later change.

The cover step spent its last pull requests closing work already done (RES-0310, conclusion 2).
