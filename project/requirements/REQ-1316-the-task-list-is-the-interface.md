---
id: REQ-1316
artifact: requirement
topic: source-control
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0002
verification: behavioural
---

# REQ-1316

Where a repository declares its tasks through a runner, the harness MUST
invoke work through those declared tasks rather than through the underlying
commands, so that the task list is the surface a repository grants and
withholds.
