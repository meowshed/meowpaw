---
reader: someone installing or running meow-lua on Pi
answers: what meow-lua provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-lua@0.1.0]
---

# @meowshed/meow-lua

Detects Lua and Neovim plugins from what git tracks, names the runtime or the editor that evaluates the code before it binds anything, prints a stages table bound from the formatter, linter, test runner and rockspec the repository configured, reports a plugin with no runtime declared or no help file, writing no file, and carries what a reviewer of Lua or of a Neovim plugin checks that no command reports. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-lua
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
