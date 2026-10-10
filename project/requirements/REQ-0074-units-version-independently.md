---
id: REQ-0074
artifact: requirement
topic: universality
class: non-functional
status: withdrawn
revised: 2026-10-10
elaborates: RES-0004
verification: static
---

# REQ-0074

**Withdrawn. Replaced by REQ-4502 and REQ-4508.**

It read: each separately installable unit MUST be installable, removable and versionable independently of every other one.

The units' programs are one program built thirteen times, so ADR-2870 ships
the one build in the core unit and has a unit depend on it (RES-0347). A unit
may depend on the core unit and on no other, which keeps the rest of the rule.
