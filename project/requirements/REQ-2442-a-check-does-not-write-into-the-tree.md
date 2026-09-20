---
id: REQ-2442
artifact: requirement
topic: packs
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0106
verification: behavioural
---

# REQ-2442

A verb MUST NOT leave files in the working tree, and where its tool writes
output by default the pack MUST direct that output outside the tree.

A check that modifies what it checks cannot be trusted about what it found.
