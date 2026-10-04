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
the same ten rules injected twice.

## Reproduction

Pi 1.0.2 on macOS 15 (aarch64), the packages at `84f8ee63`:

1. `pi install ./packages/meow-core` and `pi install ./packages/meow-flow`.
2. In a Pi session, inspect the system prompt: the reply shape appears
   twice, because both extensions pushed it.
3. `grep -l 'guidelines?.push' packages/*/extensions/*.ts` lists all six
   extensions.

## What the system does

Installing the kernel and any other layer charges the reply shape's
roughly 4,200 characters to the context twice on every turn, for no effect:
a rule stated twice in one prompt teaches the model nothing new.

## What it should do, and why

The reply shape reaches the model once per session, from the kernel
(REQ-4108), because the layering already puts it there and a second copy
duplicates a rule at full context cost.

## Triage

Enters at implement, because the requirement named the injection and said
nothing about who else may inject. Minor, because nothing breaks: the cost
is duplicate context and nothing else.

## Closed by

TSK-5206. Only `packages/meow-core/extensions/kernel.ts` pushes into
`promptGuidelines`; a session with the kernel and the flow installed
together shows the reply shape once.
