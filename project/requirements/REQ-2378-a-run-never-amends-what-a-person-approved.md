---
id: REQ-2378
artifact: requirement
topic: unattended-runs
class: functional
status: withdrawn
revised: 2026-09-27
elaborates: RES-0074
verification: behavioural
---

# REQ-2378

**Withdrawn. Replaced by REQ-2406.**

It read: an unattended run MUST NOT amend an approved requirement or withdraw
an approved decision.

It left a repository no way to lift the limit. The owner decided on
2026-09-27 that every gate is configurable, so REQ-2406 keeps the limit as the
default and lets a repository declare that its unattended runs may cross it.
