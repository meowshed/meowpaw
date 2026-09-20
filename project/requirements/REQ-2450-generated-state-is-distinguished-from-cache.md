---
id: REQ-2450
artifact: requirement
topic: packs
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0108
verification: behavioural
---

# REQ-2450

A pack MUST state which of an ecosystem's generated files are project state to
be committed and which are cache to be ignored.

Ignoring the first breaks every collaborator while working for the author, and
committing the second fills the history with regenerable noise.
