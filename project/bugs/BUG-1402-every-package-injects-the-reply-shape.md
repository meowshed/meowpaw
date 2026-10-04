---
id: BUG-1402
artifact: bug
status: approved
severity: minor
violates: REQ-4108
enters: implement
found: 2026-10-04
revised: 2026-10-04
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Every package injects the reply shape, so two inject it twice

Each of the six Pi packages shipped by EPC-2700 carries an extension that
pushes the reply shape into the system prompt guidelines on
`before_agent_start`. The kernel's layering puts the reply shape in the
kernel alone, and a person who installs the kernel and any other layer gets
the same ten rules injected twice: once from `@meowshed/meow-core`'s
extension and once from the other package's.

## Expected

The reply shape reaches the model once per session, from the kernel
(REQ-4108), because a rule stated twice in one prompt costs context twice
and teaches the model nothing new.

## Actual

`grep -l 'guidelines?.push' packages/*/extensions/*.ts` at `84f8ee63` lists
all six extensions. Installing `@meowshed/meow-core` and
`@meowshed/meow-flow` together injects `meow.md`'s text into the guidelines
twice, roughly 4,200 characters charged to every turn for no effect.

## Reproduction

1. `pi install ./packages/meow-core` and `pi install ./packages/meow-flow`.
2. In a Pi session, inspect the system prompt: the reply shape appears
   twice.
3. Compare the context cost against a session with only
   `@meowshed/meow-core` installed: the second copy adds its full length.

## Environment

Pi 1.0.2 on macOS 15 (aarch64); meowpaw at `84f8ee63`; packages
`@meowshed/meow-core` 0.4.0 and `@meowshed/meow-flow` 0.47.0 as shipped by
EPC-2700.
