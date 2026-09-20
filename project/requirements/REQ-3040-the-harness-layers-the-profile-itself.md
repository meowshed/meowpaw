---
id: REQ-3040
artifact: requirement
topic: universality
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0267
verification: behavioural
---

# REQ-3040

The harness MUST layer the profile itself rather than rely on the platform
inheriting settings from a parent directory, and a per-part profile MUST
declare what it needs rather than assume the root's.

Project settings are not inherited from parent directories although
instruction files are, and a design resting on that asymmetry breaks in one of
the two cases.
