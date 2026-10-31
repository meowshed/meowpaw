---
reader: someone installing or running meow-loop on Pi
answers: what meow-loop provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-loop@0.18.0]
---

# @meowshed/meow-loop

Runs the method's chain inside the Pi session where a person starts it: /meow-loop:run repeats /meow-flow:run until the record holds no open work, the iterations or the hours it was given (ten and four by default) are reached, two iterations change nothing or the person types anything else. Hooks hold the bounds outside the model, deny what would change a run's terms, and let only a person start a run. It keeps nothing in context on every turn. Distributed as a Pi package.

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

## Read a subcommand's help

`meow-loop --help` lists the subcommands, and `meow-loop <subcommand> --help` names
what it determines, what you read to reach the same answer without the tool,
and the first word of each kind of line it prints. A test holds each
subcommand's output to those words.

## Hooks

`prompt` starts or cancels a run from the prompt a person typed, and `stop` blocks the end of a turn while the run has work left; the `meow-loop:run` skill says why, and no gate check holds the rule yet.
`guard` stops a write into a run's own state or a status the run can't give; the `meow-loop:run` skill says why, and no gate check holds the rule yet.

## Prepare a run for a terminal

The `loop` skill writes the prompt file a run outside the session reads and
prints the `meow-loop start` command for a terminal outside the session, such
as a separate tmux window. Only a person starts a run, in either place.
