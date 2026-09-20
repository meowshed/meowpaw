---
id: REQ-2568
artifact: requirement
topic: the-forge
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0133, RES-0134
verification: behavioural
---

# REQ-2568

The harness MUST account for each limit the service imposes separately,
including limits on creating content, limits that differ by how the run is
authenticated and limits that apply only inside an automated workflow.

A write costs several times a read, so re-reading state after every write is
not a cheap safety measure.
