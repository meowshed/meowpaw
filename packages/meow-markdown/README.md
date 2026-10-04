---
reader: someone installing or running meow-markdown on Pi
answers: what meow-markdown provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-markdown@0.6.1]
---

# @meowshed/meow-markdown

Detects a Markdown corpus from what git tracks, lists the tools a repository configured for it, and prints a verbs table bound from that configuration, reports a missing render target, markdownlint settings the lint verb lacks, ignores or never applies and a link check that leaves its network behaviour undeclared, and runs lychee to report a link it couldn't reach as unreachable, never as a finding, writing no file, and carries what a reviewer of a Markdown document checks that no command reports. It keeps up to 380 characters in context on every turn. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-markdown
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
