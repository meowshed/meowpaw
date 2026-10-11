---
reader: someone installing or running meow-flow on Pi
answers: what meow-flow provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-flow@0.52.0]
---

# @meowshed/meow-flow

Runs the method's seven steps from research to review, each refused by a native program until its input is approved, routes each request before work starts, drives the steps to the next approval gate with /meow-flow:run, and checks the record they write where .meowpaw/profile.toml declares it. It keeps up to 910 characters in context on every turn. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-flow
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

## Commands

Each command sends its skill's instructions into the session, so the step
runs: the seven step commands load the method skill, `/meow-flow:run` the
driver skill, and `/meow-flow:init` and `/meow-flow:onboard` their own. Type
the command and its arguments, and the model carries out what the skill
says.

The researcher's nested call picks the model the `MEOW_NESTED_MODEL`
environment variable names before any other, so you choose what the draft
costs: it runs on glm 5.3 flash where the variable names nothing.
