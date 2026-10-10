---
reader: someone installing or running meow-author on Pi
answers: what meow-author provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-author@0.7.0]
---

# @meowshed/meow-author

Holds how Claude Code writes skills, agents, output styles, commands and prompt hooks, checks them in a repository's plugins or its own .claude directory for fixed tags, a description, the six fields an agent declares, every supporting file named and a stated stopping point, and reports each unit's context cost. It keeps up to 400 characters in context on every turn. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-author
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
