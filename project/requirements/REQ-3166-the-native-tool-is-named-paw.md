---
id: REQ-3166
artifact: requirement
topic: distribution
class: functional
status: draft
revised: 2026-09-26
elaborates: RES-0273
source: the repository owner's decision
verification: static
---

# REQ-3166

The native tool's executable MUST be named `paw`.

The name belongs to the executable alone: the units that ship it keep their
own names, so `meow-method` stays `meow-method`. Whether a unit's launcher
takes the name as well is left to the design.
