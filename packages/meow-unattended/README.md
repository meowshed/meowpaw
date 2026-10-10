---
reader: someone installing or running meow-unattended on Pi
answers: what meow-unattended provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-unattended@0.4.0]
---

# @meowshed/meow-unattended

Prints the posture an unattended run is held to from the [unattended] table a repository declares: the permission mode, the gates the run may decide, its release command and whether it may amend an approved record, with each deny rule and what the rules don't stop. It writes nothing, starts nothing and keeps nothing in context on every turn. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-unattended
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
