---
id: REQ-2078
artifact: requirement
topic: testing
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0066
verification: behavioural
---

# REQ-2078

A check that would not fail if its requirement were violated MUST be rewritten
rather than supplemented with another.

Adding a second check leaves the first one passing for the wrong reason, and
the pair now reports twice what neither establishes.
