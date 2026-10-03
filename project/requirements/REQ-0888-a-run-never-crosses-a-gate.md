---
id: REQ-0888
artifact: requirement
topic: long-runs
class: functional
status: withdrawn
revised: 2026-10-03
elaborates: RES-0024, RES-0059
source: the repository owner's decision
verification: static
---

# REQ-0888

**Withdrawn by ADR-2380. Replaced by REQ-3704 and REQ-3714.**

It read: a run MUST stay within one step, because a gate it could cross is a
gate it would cross unattended.

The owner chose that one unattended run carries the whole chain and decides
each gate itself, so a run that stayed in one step would stop at the first
approval and wait for a person who isn't there. REQ-3704 makes the run repeat
the chain until nothing is open, and REQ-3714 makes it decide each gate against
the written principles.
