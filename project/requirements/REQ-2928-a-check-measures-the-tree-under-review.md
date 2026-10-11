---
id: REQ-2928
artifact: requirement
topic: verification
class: non-functional
status: approved
revised: 2026-10-11
elaborates: RES-0031
verification: behavioural
---

# REQ-2928

A check this repository runs against its own tree MUST run the binary that
tree builds, and never an installed release of the harness.

The reason: a result attributed to the tree describes the installed binary's
behaviour where the launcher prefers the install, which is how two false
defect records were written in one day (BUG-1680). A suite that runs a unit's
launcher pins the launcher's data directory, as `meow-author`'s suite already
does, so the fallback build beside the unit is what runs.
