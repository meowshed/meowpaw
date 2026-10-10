---
id: REQ-4504
artifact: requirement
topic: shared-binary
class: functional
status: approved
revised: 2026-10-10
elaborates: RES-0347
verification: static
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-4504

A unit's launcher MUST find the shared binary through a path the platform
documents.

The cache layout isn't one: the platform may change it, and several versions of
the core unit sit in it.
