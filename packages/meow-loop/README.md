---
reader: someone installing or running meow-loop on Pi
answers: what meow-loop provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-loop@0.16.0]
---

# @meowshed/meow-loop

Repeats one prompt in fresh claude -p calls, bound to one step of the method, until the step's work is done and the verification stages a person names pass at one tree, the stated number of iterations has run, two iterations in a row change nothing or the stated number of iterations has run, with its bounds held outside the model, ends a run that changes its own terms, crosses a gate or leaves its step, and lets only a person start a run. It keeps nothing in context on every turn. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-loop
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

## Start a run

A person starts a run by typing `/meow-loop:run --iterations 5 --hours 2` in
the session. The run repeats the method's chain there, and typing any other
prompt ends it `cancelled`. Each bound has a default, so `/meow-loop:run`
alone runs up to 10 iterations and 4 hours.

## Prepare a run for a terminal

The `loop` skill writes the prompt file a run outside the session reads and
prints the `meow-loop start` command for a terminal outside the session, such
as a separate tmux window. Only a person starts a run, in either place.
