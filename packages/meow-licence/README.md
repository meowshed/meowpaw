---
reader: someone installing or running meow-licence on Pi
answers: what meow-licence provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-licence@0.4.0]
---

# @meowshed/meow-licence

Adds the licence header a repository declares to each file Claude Code creates, never rewrites one, and checks that every tracked file is covered by the licensing declared in REUSE.toml, in .meowpaw/profile.toml or in its files' headers. It keeps up to 380 characters in context on every turn. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-licence
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
