---
reader: someone installing or running meow-starlark on Pi
answers: what meow-starlark provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-starlark@0.1.0]
---

# @meowshed/meow-starlark

Detects Bazel and Buck workspaces from what git tracks, names the build system that evaluates the Starlark before it binds anything, prints a stages table bound from the buildifier configuration and the workspace file the repository committed with Bazel's symlinks switched off, reports a stage that passes whatever buildifier finds, rewrites files or leaves output in the working tree, writing no file, and carries what a reviewer of Starlark checks that no command reports. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-starlark
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

Commit the workspace markers, `MODULE.bazel` and the others, and
`.buildifier.json`: they are project state. Ignore `bazel-*`, the convenience
symlinks Bazel creates in the workspace unless `--symlink_prefix=/` stops
them, and `buck-out/`, where Buck writes its output. `status` states both
lists, and `check` reports a `buck-out` nothing ignores.
