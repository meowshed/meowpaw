---
id: TSK-5204
artifact: task
status: done
revised: 2026-10-04
epic: EPC-2700
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

## What to do

Create `packages/meow-mise/`, `packages/meow-gotask/` and
`packages/meow-markdown/`, each with its skill, its binary wrapper and a
thin extension.

## Depends on

- TSK-5200 (blocking): the authorising records, which this task
  implements.

## Evidence

PR #845: each pack builds with its skill and its wrapper; the skills load
by description and the wrappers resolve the platform binary once one is
downloaded, as TSK-5208's installer provides.

## Left alone

The packs' reply-shape injection, which BUG-1402 showed was the kernel's
alone to make; the other nine packs, which no decision asks for yet.
