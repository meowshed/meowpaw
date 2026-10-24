---
reader: someone installing or running meow-scm on Pi
answers: what meow-scm provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-scm@0.8.0]
---

# @meowshed/meow-scm

Checks a commit message against the convention the repository declares in .meowpaw/profile.toml and against a ban on crediting a tool, before the message is used, and reports an undeclared convention as undeclared, never as met. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-scm
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
