---
reader: someone installing or running meow-prose on Pi
answers: what meow-prose provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-prose@0.7.0]
---

# @meowshed/meow-prose

Holds everything Claude Code writes for you to one writing standard: the answer first, a reason for every rule, one term for one thing, and plain English for a reader who learned it as a second language. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-prose
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

## Review a text

The `meow-prose-review` tool reviews a finished text against the writing
standard, and the model calls it when a review, check, proofread or critique
is asked for. Its nested call runs on glm 5.3 flash, or the model the
`MEOW_NESTED_MODEL` environment variable names, and carries the standard and
the reply shape with it, because a nested call reads no file and holds no
skill.
