---
reader: someone installing or running meow-scheme on Pi
answers: what meow-scheme provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-scheme@0.1.0]
---

# @meowshed/meow-scheme

Detects Scheme projects from the manifests git tracks, names the implementation before it binds anything, prints a stages table that binds Racket's tests as raco test without writing bytecode and binds nothing for an implementation whose commands the repository doesn't commit, reports a stage that writes bytecode into the working tree and a compiled directory that isn't ignored, writing no file, and carries what a reviewer of Scheme checks that no command reports. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-scheme
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

Commit `info.rkt`: it is project state, and it declares which paths `raco
test` skips and includes. Ignore `compiled/`, the bytecode `raco make` and
`raco test --make` write beside each source. `status` states both for each
Racket directory, and `check` reports a `compiled/` nothing ignores or git
tracks.
