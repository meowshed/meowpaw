---
id: REQ-4148
artifact: requirement
topic: pi-packages
class: functional
status: approved
revised: 2026-10-04
elaborates: RES-0341
verification: behavioural
---

# A unit's version is one number on every agent platform

Every agent platform that ships a meowpaw unit — the Claude Code
marketplace, the npm registry, and any distribution added later — names
the unit's releases by the same version, and an install of the unit at a
version is the same content whichever harness loads it. A unit tag is cut
from the marketplace release's tree at most once per release, and the npm
registry's versions are immutable and never moved.

Rationale: ADR-2830 found the first clean release cutting three unit tags
onto the release's own tree, a deviation that no check tells apart from a
tag on the unit's own history, because the marketplace archive is rebuilt
from the tree the tag sits on. One number per unit across platforms is
what makes a version a fact about the unit rather than about a registry.
