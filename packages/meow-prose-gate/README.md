---
reader: someone installing or running meow-prose-gate on Pi
answers: what meow-prose-gate provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-prose-gate@0.4.0]
---

# @meowshed/meow-prose-gate

Stops Claude Code from publishing a commit message, pull request, issue, comment or release note that carries a writing defect any reader can point to. A program blocks a stock idiom from a fixed list, a line of bold text in place of a heading and text hidden in a file, and a model judging twice blocks other idioms, unexpanded acronyms and a bold phrase opening a paragraph only where both judgements agree on a span the text holds. It keeps nothing in context. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-prose-gate
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
