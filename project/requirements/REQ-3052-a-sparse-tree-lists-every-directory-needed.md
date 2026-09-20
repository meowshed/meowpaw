---
id: REQ-3052
artifact: requirement
topic: universality
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0267
verification: behavioural
---

# REQ-3052

Where parallel agents work in sparse working trees, the sparse paths MUST list
every directory any of them needs, including the repository's configuration
directory.

All the working trees in one session share the same paths, and a tree missing
the configuration directory has none of the repository's own settings.
