---
id: REQ-2919
artifact: requirement
topic: artifacts
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0258
verification: behavioural
---

# REQ-2919

Evidence in a defect record MUST be sanitised.

A failing log is where a credential appears, so the prohibition on handling
secret material has to survive the one place it is most likely to be broken.
