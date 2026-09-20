---
id: REQ-2424
artifact: requirement
topic: packs
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0101, RES-0104, RES-0109
verification: behavioural
---

# REQ-2424

Where a pack changes a tool's configuration, it MUST edit it as structured
data rather than as text, and MUST verify the result parses.

A structured file admits several spellings of the same thing, and a textual
edit picks the wrong one in exactly the cases that matter.
