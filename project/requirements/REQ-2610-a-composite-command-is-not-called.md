---
id: REQ-2610
artifact: requirement
topic: helpers
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0143
verification: behavioural
---

# REQ-2610

The harness MUST NOT call a command that bundles several decisions the method
reserves for itself, such as one that writes a message, commits, rebases and
removes a working tree together.
