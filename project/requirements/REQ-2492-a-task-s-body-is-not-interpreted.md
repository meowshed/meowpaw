---
id: REQ-2492
artifact: requirement
topic: runners
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0124, RES-0123
verification: behavioural
---

# REQ-2492

The harness MUST NOT infer what a task does from its body, and MUST NOT read a
task's declared dependencies as an order of execution.

A task body may be written in another language entirely, and dependencies in
at least one runner execute in parallel with documentation saying they must
not depend on one another.
