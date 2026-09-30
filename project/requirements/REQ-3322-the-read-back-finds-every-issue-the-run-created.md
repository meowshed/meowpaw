---
id: REQ-3322
artifact: requirement
topic: the-forge
class: functional
status: approved
revised: 2026-09-30
elaborates: RES-0312
verification: behavioural
---

# REQ-3322

The read-back of the issues a projection run created MUST include every such
issue the tracker still holds, whichever request was the run's first.

A created issue the read-back misses is reported as not read back, so a run
that did all its work reports a partial result.
