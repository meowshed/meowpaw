---
reader: someone installing or running meow-prose on Pi
answers: what meow-prose provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-prose@0.5.1]
---

# @meowshed/meow-prose

Holds everything Claude Code writes for you to one writing standard: the answer first, a reason for every rule, one term for one thing, and plain English for a reader who learned it as a second language. It keeps up to 700 characters in context on every turn, and loads a skill of about 5,000 tokens each time you write. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-prose
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
