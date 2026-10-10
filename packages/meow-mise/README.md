---
reader: someone installing or running meow-mise on Pi
answers: what meow-mise provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-mise@0.2.1]
---

# @meowshed/meow-mise

Reports the tasks mise resolves in a repository, with where each came from and what stops a stage running it unattended, binds the stages to them, and never grants trust, answers a prompt or writes a file. It keeps up to 380 characters in context on every turn. Distributed as a Pi package.

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
