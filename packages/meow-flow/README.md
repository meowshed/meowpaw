---
reader: someone installing or running meow-flow on Pi
answers: what meow-flow provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-flow@0.49.0]
---

# @meowshed/meow-flow

Runs the method's seven steps from research to review, each refused by a native program until its input is approved, routes each request before work starts, drives the steps to the next approval gate with /meow-flow:run, and checks the record they write where .meowpaw/profile.toml declares it. It keeps up to 820 characters in context on every turn. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-flow
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
