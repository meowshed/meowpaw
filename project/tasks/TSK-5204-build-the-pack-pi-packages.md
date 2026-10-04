---
id: TSK-5204
artifact: task
status: done
revised: 2026-10-04
realises: ADR-2780
closes: [REQ-4100, REQ-4102, REQ-4106, REQ-4114, REQ-4118, REQ-4120]
issue: 839
---

# Build the pack Pi packages

Create `packages/pi-mise/`, `packages/pi-gotask/` and `packages/pi-markdown/`,
each with a thin extension that resolves its binary and carries its skill.

## Acceptance criteria

1. Each pack installs and its skill loads by description. Closed by: manual
   session test.
2. `meow-mise`, `meow-gotask` and `meow-markdown` run from their packages and
   report verb bindings. Closed by: running each binary's status command.
