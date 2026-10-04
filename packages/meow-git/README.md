---
reader: someone installing or running meow-git on Pi
answers: what meow-git provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-git@0.3.0]
---

# @meowshed/meow-git

Refuses a git commit on the trunk the repository declares, and checks every commit a push would publish for the declared commit convention and for a good signature, before the push runs. It keeps nothing in context on every turn. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-git
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
