---
id: REQ-2542
artifact: requirement
topic: source-control
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0132
verification: behavioural
---

# REQ-2542

Where a source-control tool has no read-only invocation, the harness MUST
inspect through the read-only commands of the tool beneath it.

In at least one of them every command snapshots and commits the working copy,
so inspecting with it changes the thing being inspected.
