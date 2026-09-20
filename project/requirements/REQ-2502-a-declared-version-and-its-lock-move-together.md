---
id: REQ-2502
artifact: requirement
topic: runners
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0122
verification: behavioural
---

# REQ-2502

Where the harness changes a declared tool version, it MUST update the lock
recording the resolved version in the same change.

Otherwise a fresh machine resolves a different version from the one that was
tested.
