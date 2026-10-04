---
reader: someone installing or running the meowpaw practice layer on Pi
answers: what meow-code provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-code@0.6.2]
---

# @meowshed/meow-code

The meowpaw practice layer: how code is changed, checked and debugged; how
skills, agents and prompts are authored; and how licence headers are applied
and checked. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-code
```

The npm tarball carries the meow binary for every platform, so the install
makes no request and needs no checkout. Installing from this repository's
checkout is the development install: it loads the package in place, runs no
lifecycle script, and the person installing it runs `node install-meow.mjs`
by hand to fetch the binary for their machine.

```bash
pi install packages/meow-code   # development install, from the checkout
```

## What it does

### Changing code

The `change` skill holds how Claude Code makes the smallest correct change,
writes a check seen failing and keeps each edit to one purpose.

### Debugging

The `debug` skill holds how Claude Code reproduces a defect before offering a
cause, tests one hypothesis at a time and fixes the most probable accident
first.

### Authoring

The `write` skill holds how Claude Code writes skills, agents, output styles,
commands and hooks, checks them and reports each unit's context cost.

### Licensing

The `header` skill holds how Claude Code adds the licence header a repository
declares, never rewrites an existing one, and checks that every tracked file
is covered.

## Binaries

The package carries shell wrappers for `meow-author` and `meow-licence`. Each
wrapper resolves the platform-specific `meow` binary at runtime and runs it
with the unit's subcommand.
