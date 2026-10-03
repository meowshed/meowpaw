---
id: REQ-2374
artifact: requirement
topic: unattended-runs
class: functional
status: withdrawn
revised: 2026-10-03
elaborates: RES-0074
source: the repository owner's decision
verification: behavioural
---

# REQ-2374

**Withdrawn by ADR-2380. Replaced by REQ-3716 and REQ-3722.**

It read: an unattended run MUST NOT take an action whose reversal costs more
than a revert, because reversibility separates a night approval a morning
reader can disagree with from one they are stuck with.

The owner chose that unattended mode works fully without a person, so it
merges and releases its own work. REQ-3716 lists every such action in the
run's report for the person to audit, and REQ-3722 limits a release to the
command the profile declares.
