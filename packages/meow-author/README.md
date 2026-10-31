---
reader: someone installing or running meow-author on Pi
answers: what meow-author provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-author@0.10.1]
---

# @meowshed/meow-author

Holds how Pi writes skills, agents, output styles, commands and prompt hooks, checks them in a repository's plugins or its own .claude directory for fixed tags, a description, the six fields an agent declares, every supporting file named and a stated stopping point. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-author
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

## What it checks in the tools a unit grants

Each tool an agent's `tools` or a skill's `allowed-tools` grants must have a
step named beside it in the unit's README, under `## Tools`, as a list item
that opens with the tool in code font, a colon and what the step does with it.
A tool with no such item fails the check, naming the file, the tool and the
README, so a tool no step needs is visible and removed.

## What each unit loads

`meow-author check` also reads each unit's always-loaded material, and fails
on a skill's or agent's description and its `when_to_use` together over the
platform's cap of 1,536 characters, which the platform sets. How
often each skill is used comes from `/skill-doctor` in Pi; the unit
reads none of Pi's own files.

## What it costs you The

check is a native binary shipped inside
the unit, so it needs nothing installed on the machine.

## Read a subcommand's help

`meow-author --help` lists the subcommands, and `meow-author <subcommand> --help` names
what it determines, what you read to reach the same answer without the tool,
and the first word of each kind of line it prints. A test holds each
subcommand's output to those words.
