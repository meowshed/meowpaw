---
reader: someone installing or running meow-code on Pi
answers: what meow-code provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-code@0.5.0]
---

# @meowshed/meow-code

Holds how Pi changes code, writes a check and debugs a defect: the smallest correct change, the most precise edit, checks seen failing, and a defect reproduced before any cause is offered. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-code
```

The paw executable ships with `@meowshed/meow-core` alone (REQ-4612): this
package's launchers run their subcommands through it, so install the core
package beside this one for the binary-backed checks. Without it, every
check reports unrun and lets the command through.

```bash
pi install npm:@meowshed/meow-core   # carries the binary the launchers run
```

Installing from this repository's checkout is the development install: it
loads the package in place and runs no lifecycle script.

## What it adds to a session

Before Pi changes code or writes a check, it loads the
`meow-code:change` skill, which has it:

- make the smallest change that is correct, and never reformat while it
  changes behaviour;
- read a file before writing to it, and batch reads and edits that don't
  depend on each other;
- ask a language server about a symbol where the session offers one, and say
  what a text search can't cover where it offers none;
- prefer a semantic edit for a symbol, a structural one for a mechanical
  rewrite and a textual one only for a literal;
- read a file's diagnostics after editing it, and take its evidence from your
  verification stages, never from the diagnostics;
- document every declaration another module or a user can reach, preferring
  an example the language runs as a check;
- check what it can statically before behaviourally, and behaviourally before
  by evaluation, and see a check fail before the work that makes it pass;
- report a check that couldn't fail as a defect, and rewrite it instead of
  adding a second one;
- run mutation testing through the tool you or a pack names, when you ask
  whether the checks would catch a change.

Before Pi looks for the cause of a bug, a failing check, a crash or a
wrong output, it loads the `meow-code:debug` skill, which has it:

- reproduce the defect first, as small as it can, and keep the reproduction;
- record what the system actually does before offering a cause;
- hold one hypothesis at a time and try to refute it, and bisect once the
  hypotheses run out;
- close the defect on the reproduction failing before the fix and passing
  after it, and fix the cause, saying so where it treated only the symptom;
- stop and ask for an amendment where the defect shows a requirement to be
  wrong, and patch nothing.

You don't invoke either skill yourself: Pi loads it from its
description whenever it's about to change code.

## What it costs you Each

skill's body loads only when Pi changes code or debugs. The unit ships
no program.
