---
id: REQ-1830
artifact: requirement
topic: stacked-changes
class: functional
status: approved
revised: 2026-09-20
unit: U-0001
elaborates: RES-0065
verification: behavioural
---

# REQ-1830

Where a layer of a stack is closed or ejected from a merge queue, the harness
MUST report every task above it as blocked, naming the layer that blocked
them.
