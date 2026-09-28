---
id: REQ-3214
artifact: requirement
topic: the-method
class: functional
status: approved
revised: 2026-09-27
elaborates: RES-0075
verification: evaluation
---

# REQ-3214

The cover step MUST run in a context separate from the one that implements
the task.

The platform's own guidance has one context write the tests and another the
code, so that neither is written from the other's reasoning.
