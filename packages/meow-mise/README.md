---
reader: someone installing or running meow-mise on Pi
answers: what meow-mise provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-mise@0.2.0]
---

# @meowshed/meow-mise

The meowpaw mise pack for Pi: reports the tasks mise resolves in a
repository, with where each came from and what stops a verb running it
unattended, binds the verbs to them, and never grants trust, answers a
prompt or writes a file.

## Install it

```bash
pi install npm:@meowshed/meow-mise
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
pi install packages/meow-mise   # development install, from the checkout
```

## What it does

### The tasks skill

The `tasks` skill holds how the session binds the verification verbs —
format, lint, check, test and build — to the tasks mise resolves, and what
it reports about each: where the task came from and what keeps it from
running unattended.

### The binary

The `meow-mise` wrapper resolves the platform meow binary and runs
`meow mise`, which reports the resolved tasks and binds the verbs from the
profile declaration. It never grants trust, answers a prompt or writes into
the repository.
