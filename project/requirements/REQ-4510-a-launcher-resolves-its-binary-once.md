---
id: REQ-4510
artifact: requirement
topic: shared-binary
class: non-functional
status: approved
revised: 2026-10-11
elaborates: RES-0354
verification: behavioural
---

# REQ-4510

A unit's launcher MUST resolve its binary's path once per machine and reuse
the resolution, never re-probing the machine or walking the core unit's data
directory on every guarded call.
