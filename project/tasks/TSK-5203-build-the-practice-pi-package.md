---
id: TSK-5203
artifact: task
status: done
revised: 2026-10-04
epic: EPC-2700
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

## What to do

Create `packages/meow-code/` with the practice extension, the change,
debug, write and header skills, and the author and licence wrappers.

## Depends on

- TSK-5200 (blocking): the authorising records, which this task
  implements.

## Evidence

PR #845: the package builds with the four skills and the two binary
wrappers; the skills load by description and the wrappers resolve the
platform binary once one is downloaded, as TSK-5208's installer provides.

## Left alone

The practice extension's reply-shape injection, which BUG-1402 showed was
the kernel's alone to make, and which this task's extension now omits.
