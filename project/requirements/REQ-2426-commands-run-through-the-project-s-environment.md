---
id: REQ-2426
artifact: requirement
topic: packs
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0103, RES-0104, RES-0108
verification: behavioural
---

# REQ-2426

Where a project declares an environment or a package manager, the pack MUST
invoke tools through it rather than through whatever the shell resolves.

Otherwise the result depends on shell state nobody recorded, and the same
command passes on one machine and fails on another for no reason in the code.
