---
reader: someone installing or running meow-checks on Pi
answers: what meow-checks provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-checks@0.10.0]
---

# @meowshed/meow-checks

Runs a repository's five verification stages, format, lint, check, test and build, from the commands it declares in .meowpaw/profile.toml, and reports a stage with no command as unresolved, never as passed. It keeps up to 450 characters in context on every turn. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-checks
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
