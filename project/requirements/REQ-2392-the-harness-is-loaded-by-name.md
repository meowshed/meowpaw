---
id: REQ-2392
artifact: requirement
topic: unattended-runs
class: functional
status: withdrawn
revised: 2026-10-03
elaborates: RES-0074
source: the repository owner's decision
verification: static
---

# REQ-2392

**Withdrawn by ADR-2380. Replaced by REQ-3700.**

It read: an unattended run MUST load the harness by name rather than by
discovery, because the scripted mode that skips a folder's own hooks also
skips plugins.

It held while a run was a scripted `claude -p` process the plan composed. The
owner chose to run inside the session a person already works in, which has
loaded its plugins before the run starts, so no run composes a harness to load.
REQ-3700 places the run in that session.
