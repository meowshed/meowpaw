---
reader: someone installing or running meow-rust on Pi
answers: what meow-rust provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-rust@0.1.0]
---

# @meowshed/meow-rust

Detects Rust from the manifests git tracks, reports each manifest's edition, the pinned toolchain and the clippy groups a lint stage runs, prints a stages table bound from the cargo commands the manifests call for, reports an edition, a lint inheritance or an ignore file a manifest leaves unsaid, and compares the pinned toolchain with the installed one, writing no file, and carries what a reviewer of Rust checks that no command reports. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-rust
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

The package puts its launcher on `PATH`, so the skill runs `meow-rust status`,
`meow-rust bind`, `meow-rust check` and `meow-rust toolchain` in your
repository. They behave as the Claude Code unit's page describes in
`plugins/meow-rust/README.md`: `status` lists each manifest, `bind` prints a
`[stages]` table bound from the manifests, `check` reports an edition, a lint
inheritance or an ignore file a manifest leaves unsaid, and `toolchain`
compares your pinned toolchain with the installed one.

## Generated files

Commit `Cargo.toml`, `Cargo.lock`, the toolchain file, `.config/nextest.toml`
and any `rustfmt.toml` or `clippy.toml`, because each is project state. Ignore
`target/`, the cache cargo writes at the workspace's root, because it is
regenerated on the next build.

## What it needs

git, and `rustc` on `PATH` for `toolchain`. The pack is current as of Rust
1.99, Cargo 1.99 and clippy's lint groups as the rust-clippy README lists them
on 2026-10-13.
