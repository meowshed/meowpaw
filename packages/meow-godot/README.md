---
reader: someone installing or running meow-godot on Pi
answers: what meow-godot provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-godot@0.1.0]
---

# @meowshed/meow-godot

Detects Godot projects from what git tracks, reads the engine version from each project file before it binds anything, prints a stages table bound from the gdtoolkit, GUT and export preset files the repository committed with an import before every export and its output outside the working tree, reports an engine cache or identifier file ignored or committed wrongly, writing no file, and carries what a reviewer of GDScript and scenes checks that no command reports. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-godot
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

## Generated files

Commit `*.import` files and, from Godot 4.4, `*.uid` files: they are project
state, and ignoring the identifiers gives every clone fresh ones, so scene
links to scripts break for everyone but the author. Ignore `.godot/`, the
engine's cache. The ignore list for Godot 3 and 4.0 differs entirely from
later versions, so check the engine version before you copy a `.gitignore`.
`status` states both lists for each project, and `check` reports a file on the
wrong side.
