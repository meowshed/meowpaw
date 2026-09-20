---
id: REQ-2620
artifact: requirement
topic: helpers
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0143
verification: behavioural
---

# REQ-2620

Where the harness shares files between working trees it MUST share only
ignored build output, never tracked source, and MUST report where the
filesystem cannot support the sharing.
