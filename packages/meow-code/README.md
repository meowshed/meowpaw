---
reader: someone installing or running meow-code on Pi
answers: what meow-code provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-code@0.4.0]
---

# @meowshed/meow-code

Holds how Claude Code changes code, writes a check and debugs a defect: the smallest correct change, the most precise edit, checks seen failing, and a defect reproduced before any cause is offered. Distributed as a Pi package.

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
