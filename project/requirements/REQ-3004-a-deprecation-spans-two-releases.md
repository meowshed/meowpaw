---
id: REQ-3004
artifact: requirement
topic: distribution
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0264
verification: behavioural
---

# REQ-3004

A deprecation MUST be announced in one release and removed in a later one, and
a deprecated front-matter field MUST be accepted alongside its replacement
throughout that window.

It lets a user upgrade, remove what is deprecated, and upgrade again; and what
breaks here is a corpus somebody already wrote rather than a caller who can be
changed.
