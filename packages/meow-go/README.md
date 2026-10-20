---
reader: someone installing or running meow-go on Pi
answers: what meow-go provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-go@0.1.0]
---

# @meowshed/meow-go

Detects Go from the modules git tracks, reports each module's language version, pinned toolchain, declared tools and golangci-lint configuration, prints a stages table bound from them with the race detector on in test, reports a golangci-lint configuration that is not the version 2 shape and states a supply-chain check's reach, and compares the pinned toolchain with the installed one, writing no file, and carries what a reviewer of Go checks that no command reports. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-go
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

## Run it

The package puts its launcher on `PATH`, so the skill runs `meow-go status`,
`meow-go bind`, `meow-go check` and `meow-go toolchain` in your repository.
They behave as the Claude Code unit's page describes in
`plugins/meow-go/README.md`: `status` lists each module, `bind` prints a
`[stages]` table with the race detector on in `test`, `check` reports a
golangci-lint configuration that is not the version 2 shape, and `toolchain`
compares your pinned toolchain with the installed one.

## Generated files

Commit `go.mod`, `go.sum`, `go.work`, `go.work.sum`, your golangci-lint
configuration and a `vendor/` directory if you vendor, because each is project
state. Ignore `*.test` binaries and coverage profiles, because each is
regenerated on the next run.

## What it needs

git, and `go` on `PATH` for `toolchain`. The pack is current as of Go 1.26 and
the golangci-lint v2 configuration shape its migration guide describes, read on
2026-09-20.
