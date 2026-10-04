---
id: TSK-5203
artifact: task
status: done
revised: 2026-10-04
realises: ADR-2780
closes: [REQ-4100, REQ-4102, REQ-4106, REQ-4114, REQ-4118, REQ-4120]
issue: 838
---

# Build the practice Pi package

Create `packages/pi-practice/` with the practice extension that resolves the
author and licence binary paths. Carry the change, debug, write and header
skills.

## Acceptance criteria

1. `pi install` loads the practice extension, and each skill loads by
   description. Closed by: manual session test invoking each skill.
2. `meow-author check` runs from the package and reports authoring findings.
   Closed by: running the check on a fixture.
3. `meow-licence` runs from the package and reports coverage findings. Closed
   by: running the check on a fixture.
