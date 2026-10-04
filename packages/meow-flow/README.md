---
reader: someone installing or running the meowpaw method on Pi
answers: what meow-flow provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-flow@0.47.0]
---

# @meowshed/meow-flow

The meowpaw method: the seven-step chain, record checking, commit
convention, git guards, loop runner, unattended planning and GitHub governance
guard. It drives the method, checks the record and protects the repository.

## Install it

```bash
pi install npm:@meowshed/meow-flow
```

The meow binary ships with `@meowshed/meow-core` alone (REQ-4144): this
package's launchers run their subcommands through it, so install the core
package beside this one for the binary-backed checks. Without it, every
check reports unrun and lets the command through.

```bash
pi install npm:@meowshed/meow-core   # carries the binary the launchers run
```

Installing from this repository's checkout is the development install: it
loads the package in place and runs no lifecycle script.

```bash
pi install packages/meow-flow   # development install, from the checkout
```

## What it does

### The seven-step chain

Commands `/meow-flow:research` through `/meow-flow:review` run one step each.
`/meow-flow:run` drives the chain to the next approval gate. Each step reads
its input through `paw ready` and writes its artifact from `paw template`.

### The router

The `meow-router` tool routes each request before work starts. It makes a
nested model call with Read, Grep and Glob, constrained to a read-only
dispatch that writes nothing.

### The guards

- **Git commit guard**: blocks commits on the declared trunk.
- **Git push guard**: blocks pushes of unsigned or unconventional commits.
- **Governance guard**: asks before a `gh` command changes repository
  governance.
- **Loop guard**: blocks writes that would leave a run's step or state.

### The record

`paw check` verifies front matter, identifiers, relations, coverage and shape.
`paw status --waiting` reports what sits at a gate at session start.

## Binaries

The package carries shell wrappers for `paw`, `meow-git`, `meow-github`,
`meow-loop`, `meow-scm`, `meow-checks` and `meow-unattended`. Each wrapper
resolves the platform-specific `meow` binary at runtime and runs it with the
unit's subcommand.
