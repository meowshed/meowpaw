---
id: TSK-5201
artifact: task
status: done
revised: 2026-10-04
realises: ADR-2780
closes: [REQ-4100, REQ-4102, REQ-4106, REQ-4108, REQ-4112, REQ-4114, REQ-4116, REQ-4118, REQ-4120]
issue: 836
---

# Build the kernel Pi package

Create `packages/pi-core/` with the kernel extension that injects the reply
shape and intercepts commit, PR, issue and release commands for the prose
gate. Carry the writing skill and the prose gate binary.

## Acceptance criteria

1. `pi install` from the package directory loads the kernel extension, and a
   Pi session shows the reply shape in the system prompt. Closed by: manual
   session test.
2. A `git commit` with a prose defect is blocked. Closed by: session test
   committing a message with a known defect.
3. A `gh pr create` with a prose defect is blocked. Closed by: session test.
4. The two-judge nested model call blocks only where both judgements agree.
   Closed by: session test with text that one judge flags and the other does
   not.
5. The writing skill loads by description and produces the same guidance as
   the Claude Code plugin. Closed by: manual comparison.
