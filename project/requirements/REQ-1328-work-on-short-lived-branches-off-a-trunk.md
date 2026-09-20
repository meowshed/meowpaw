---
id: REQ-1328
artifact: requirement
topic: source-control
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0002
verification: behavioural
---

# REQ-1328

Work MUST happen on short-lived branches taken from a single long-lived trunk,
and the harness MUST NOT maintain a parallel long-lived branch.

A branch that lives longer than the change it carries accumulates divergence
nobody sees until merging it is expensive, and an agent working on one cannot
notice that from inside it.
