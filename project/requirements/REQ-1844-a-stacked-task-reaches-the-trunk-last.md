---
id: REQ-1844
artifact: requirement
topic: stacked-changes
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0065
verification: static
unit: U-0001
---

# REQ-1844

A stacked task MUST merge into the branch it targets rather than into the
trunk directly, and reaches the trunk when every layer below it has merged.

The squashed commit REQ-1306 requires is per task either way.
