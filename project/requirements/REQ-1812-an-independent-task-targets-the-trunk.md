---
id: REQ-1812
artifact: requirement
topic: stacked-changes
class: functional
status: approved
revised: 2026-09-20
unit: U-0001
elaborates: RES-0065
verification: static
---

# REQ-1812

A task with no unmerged dependency MUST open its pull request against the
trunk, so that parallel work stays parallel and a stack is never deeper than
the dependencies require.
