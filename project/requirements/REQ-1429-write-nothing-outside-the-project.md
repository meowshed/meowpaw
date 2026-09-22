---
id: REQ-1429
artifact: requirement
topic: safety
class: non-functional
status: draft
revised: 2026-09-22
elaborates: RES-0271
verification: static
---

# REQ-1429

The harness MUST NOT modify files outside the repository except its own run
state and the record at the location the repository declares.

The record is the project's own material wherever the repository keeps it, and
every other file outside the repository belongs to somebody else.
