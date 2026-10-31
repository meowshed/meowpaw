---
id: TSK-5201
artifact: task
status: done
revised: 2026-10-04
epic: EPC-2700
closes:
  [
    REQ-4100,
    REQ-4102,
    REQ-4106,
    REQ-4108,
    REQ-4112,
    REQ-4114,
    REQ-4116,
    REQ-4118,
    REQ-4120,
  ]
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

## What to do

Create `packages/meow-core/` with the kernel extension, the writing skill,
the prose gate wrapper and its budget, from the spec's kernel section.

## Depends on

- TSK-5200 (blocking): the authorising records and the spec's kernel
  section, which this task implements.

## Evidence

PR #841: the package builds with the kernel extension, the writing skill
and the prose gate wrapper; the session tests the acceptance criteria
named were recorded against in BUG-1400 as never run outside the monorepo,
and TSK-5206 closes them for real.

## Left alone

The prompt bundling and PATH exposure, which BUG-1400 and BUG-1401 showed
the shipped form lacked, and which TSK-5206 and TSK-5207 hold.
