---
id: REQ-2954
artifact: requirement
topic: routing
class: functional
status: withdrawn
revised: 2026-10-03
elaborates: RES-0261
verification: static
---

# REQ-2954

**Withdrawn by ADR-2740. Replaced by REQ-3800.**

It read: the profile's format MUST permit comments and MUST share the record's
front matter shape.

TOML permits the comments the profile needs, but it deliberately differs from
the record's YAML front matter. REQ-3800 keeps the obligation that still
holds without preserving the contradiction.
