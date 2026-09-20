---
id: REQ-2396
artifact: requirement
topic: unattended-runs
class: non-functional
status: approved
revised: 2026-09-20
elaborates: RES-0074
verification: static
---

# REQ-2396

An unattended run MUST have both filesystem and network isolation in force.

Without network isolation a compromised run exfiltrates keys, and without
filesystem isolation it writes its way to the network; either one alone leaves
the other path open.
