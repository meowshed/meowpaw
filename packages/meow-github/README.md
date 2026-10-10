---
reader: someone installing or running meow-github on Pi
answers: what meow-github provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-github@0.15.0]
---

# @meowshed/meow-github

Reads a GitHub repository's issues, pull requests and comments through gh as one JSON document, projects an approved epic's tasks onto issues and writes nothing else, and asks before a Bash command's gh changes how the repository is governed. It keeps nothing in context on every turn. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-github
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
