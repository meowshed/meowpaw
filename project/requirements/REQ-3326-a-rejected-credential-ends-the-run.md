---
id: REQ-3326
artifact: requirement
topic: the-forge
class: functional
status: approved
revised: 2026-09-30
elaborates: RES-0312
verification: behavioural
---

# REQ-3326

When the tracker rejects the run's credential, the run MUST send no further
request with it.

Several rejected requests in a short time make the tracker reject the
account's valid credentials too, for a period it doesn't state.
