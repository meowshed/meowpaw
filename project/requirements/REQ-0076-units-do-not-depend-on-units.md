---
id: REQ-0076
artifact: requirement
topic: universality
class: non-functional
status: withdrawn
revised: 2026-10-10
elaborates: RES-0004
verification: static
---

# REQ-0076

**Withdrawn. Replaced by REQ-4502.**

It read: a separately installable unit MUST NOT require another such unit.

The units' programs are one program built thirteen times, so ADR-2870 ships
the one build in the core unit and has a unit depend on it (RES-0347). A unit
may depend on the core unit and on no other, which keeps the rest of the rule.
