---
id: REQ-2470
artifact: requirement
topic: runners
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0123, RES-0124
verification: behavioural
---

# REQ-2470

Where a runner may skip work as up to date, the harness MUST report which
freshness method decided it.

A timestamp comparison in a fresh checkout reports a property of the clone
rather than of the work.
