---
id: REQ-3180
artifact: requirement
topic: adoption
class: non-functional
status: approved
revised: 2026-09-21
elaborates: RES-0023
verification: static
---

# REQ-3180

A unit MUST NOT write into the repository it works on in order to run its own
capabilities, and anything it must keep MUST live inside the unit or in the
per-unit directory the platform provides.

A repository that installed one plugin agreed to that install and to nothing
else. It did not agree to carry the plugin's configuration, its task
definitions or its state in its own tree, and a unit writing them there has
modified somebody's project to suit itself.
