---
id: REQ-3176
artifact: requirement
topic: source-control
class: functional
status: approved
revised: 2026-09-21
elaborates: RES-0014
verification: static
---

# REQ-3176

A record MUST cite the pull request that carried a change, and MUST NOT cite
the commit hash, including in a field naming the revision a check ran at.

A hash is rebuilt by any rewrite of the message or the history, so a record
citing one loses its evidence the first time somebody corrects a subject. A
pull request number survives a rewrite, and the commits it merged are reachable
from it.
