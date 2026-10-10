---
reader: someone installing or running meow-loop on Pi
answers: what meow-loop provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-loop@0.13.0]
---

# @meowshed/meow-loop

Repeats one prompt in fresh claude -p calls, bound to one step of the method, until the step's work is done and the verification stages a person names pass at one tree, the stated number of iterations has run, the next call could pass the stated budget or two iterations in a row change nothing, with its bounds held outside the model, ends a run that changes its own terms, crosses a gate or leaves its step, and lets only a person start a run. It keeps nothing in context on every turn. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-loop
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
