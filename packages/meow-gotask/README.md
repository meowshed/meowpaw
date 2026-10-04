---
reader: someone installing or running meow-gotask on Pi
answers: what meow-gotask provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-gotask@0.2.0]
---

# @meowshed/meow-gotask

The meowpaw go-task pack for Pi: reports the tasks Task (go-task) resolves
in a repository, with where each came from and what stops a verb running it
unattended, binds the verbs to them, and never trusts a remote Taskfile,
answers a prompt or writes into the repository.

## Install it

```bash
pi install npm:@meowshed/meow-gotask
```

The npm tarball carries the meow binary for every platform, so the install
makes no request and needs no checkout. Installing from this repository's
checkout is the development install: it loads the package in place, runs no
lifecycle script, and the person installing it runs `node install-meow.mjs`
by hand to fetch the binary for their machine.

```bash
pi install packages/meow-gotask   # development install, from the checkout
```

## What it does

### The tasks skill

The `tasks` skill holds how the session binds the verification verbs —
format, lint, check, test and build — to the tasks go-task resolves, and
what it reports about each: where the task came from and what keeps it from
running unattended.

### The binary

The `meow-gotask` wrapper resolves the platform meow binary and runs
`meow gotask`, which reports the resolved tasks and binds the verbs from
the profile declaration. It never trusts a remote Taskfile, answers a
prompt or writes into the repository.
