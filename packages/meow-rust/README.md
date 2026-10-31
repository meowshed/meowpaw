---
reader: someone installing or running meow-rust on Pi
answers: what meow-rust provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-rust@0.2.0]
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

## Bind your stages

`meow-rust bind` prints a `[stages]` table for you to paste into
`.meowpaw/profile.toml`, and never writes the profile itself:

```toml
[stages]
format = "cargo fmt --check"
lint = "cargo clippy --all-targets -- -D warnings"
# clippy groups run: correctness, suspicious, style, complexity, perf
check = "cargo check --all-targets"
test = "cargo test"
build = "cargo build"
```

The pack binds each stage from the manifests alone, and never from what is
installed:

| Stage    | Bound to                                                    | When                             |
| -------- | ----------------------------------------------------------- | -------------------------------- |
| `format` | `cargo fmt --check`                                         | Always                           |
| `lint`   | `cargo clippy --all-targets -- -D warnings`                 | Always                           |
| `check`  | `cargo check --all-targets`                                 | Always                           |
| `test`   | `cargo nextest run`, then `cargo test --doc` with a library | A tracked `.config/nextest.toml` |
| `test`   | `cargo test`                                                | No nextest configuration         |
| `build`  | `cargo build`                                               | Always                           |

Where the top manifest isn't at the root, each command takes
`--manifest-path <file>`. Where it has a `[workspace]` table, each command takes
`--workspace` and `format` takes `--all`. Where a manifest in the workspace declares
`[features]`, `lint`, `check`, `test` and `build` take `--all-features`, so
code behind a feature is compiled in some stage. No stage checks a
combination of features short of all of them.

`lint` turns on no clippy group. `-D warnings` fails the stage on the warnings
the groups already report, and the comment under `lint` names the groups: the
five clippy runs by default, `correctness`, `suspicious`, `style`,
`complexity` and `perf`, less each your manifest sets to `allow`, plus each
other group it raises. `--all-targets` puts tests, examples and benchmarks
under the same policy as the library.

cargo-nextest runs no doctests. Where you configured it and the workspace has a
library, the `test` stage runs `cargo test --doc` after it, and a crate with no
library has no doctests to run. A repository with two or more manifests outside
one workspace gets every stage printed as unresolved, because no one cargo
command reaches both. A stage your profile already declares is left out, and a
`mise.toml` or a `Taskfile.yml` is named with the runner's pack.

## Check your settings

`meow-rust check` reports each setting your stages depend on that a manifest
leaves unsaid, one line for each finding, and exits 1 on any:

| Line                                                                               | When                                                                                             |
| ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `<file>: no edition, so cargo compiles it as the 2015 edition`                     | A `[package]` table declares no `edition`                                                        |
| `<file> doesn't inherit the workspace's lints: set workspace = true under [lints]` | The top manifest has `[workspace.lints]` and a member's `[lints]` doesn't set `workspace = true` |
| `<target> isn't ignored, and cargo writes its build output there`                  | No ignore file your repository tracks covers `target`                                            |

`<target>` is `target` at the root and `<directory>/target` below it. A global
excludes file and `.git/info/exclude` protect one clone only, so neither counts
as ignoring it. With no finding it prints `no findings`
and the groups of settings it checked, then `clippy groups:` with the groups
your `lint` stage runs.

## Compare the toolchain

`meow-rust toolchain` reads the `channel` of the `rust-toolchain` or
`rust-toolchain.toml` file nearest your top manifest, `rust-toolchain` first
where one directory holds both, and runs `rustc --version` there, where
rustup's proxy runs the toolchain that file selects. It is the one command that
starts a tool.

| Line                                                     | Means                                                 | Exit |
| -------------------------------------------------------- | ----------------------------------------------------- | ---- |
| `toolchain: nothing pinned`                              | No toolchain file                                     | 0    |
| `toolchain: <file> pins the stable channel, no version`  | A channel such as `stable` or `nightly`               | 0    |
| `toolchain: rust 1.99.0, pinned in <file> and installed` | The installed version matches, to the pin's precision | 0    |
| `unresolved: rust 1.80.0 pinned, 1.99.0 installed`       | The installed version differs                         | 3    |
| `unresolved: rust 1.80.0 pinned, none installed: ...`    | `rustc` exited non-zero, and its line follows         | 3    |
| `tool absent: rustc`                                     | `rustc` isn't on `PATH`                               | 3    |
| `tool broken: rustc printed ...`                         | `rustc` printed no version                            | 3    |

A pin of `1.99` holds every `1.99.x`.

## Generated files

Commit `Cargo.toml`, `Cargo.lock`, the toolchain file, `.config/nextest.toml`
and any `rustfmt.toml` or `clippy.toml`, because each is project state. Ignore
`target/`, the cache cargo writes at the workspace's root, because it is
regenerated on the next build.

## What it reports instead of a table

Every command exits 0 when it reports what it was asked, `check` exits 1 on a
finding, and every command exits 3 when it can't:

| Line                                              | Means                                                      |
| ------------------------------------------------- | ---------------------------------------------------------- |
| `unresolved: not a Rust repository`               | Git tracks no `Cargo.toml`                                 |
| `unresolved: no profile at .meowpaw/profile.toml` | The repository has no profile                              |
| `unresolved: the profile doesn't parse: ...`      | The profile isn't valid TOML; the parser's message follows |
| `unresolved: <file> doesn't parse as TOML: ...`   | A manifest isn't valid TOML                                |

`bind` exits 0 whatever comments its table holds, because a stage printed with
its reason is settled.

## Review Rust

When Pi reviews Rust, the skill has it run `status` first, and then
load `reviewing.md`, which holds six points no command reports: ownership as a
design choice, the error boundary, `unwrap` and `expect` outside tests, feature
combinations, the invariant beside each `unsafe` block, and the public surface.
The skill never enables clippy's `pedantic` group wholesale, never writes
`#![deny]` into source, never binds `test` to cargo-nextest alone, and never
reports a licence or advisory finding as a lint.

## What it costs you

The skill's description stays in context on every turn, and `reviewing.md`
costs context only when Rust is reviewed. The program is a native binary
shipped inside the unit, and needs git on the machine. On a machine the unit
carries no binary for, it reports the repository as unresolved and exits 3.

## Read a subcommand's help

`meow-rust --help` lists the subcommands, and `meow-rust <subcommand> --help`
names what it determines, what you read to reach the same answer without the
tool, and the first word of each kind of line it prints. A test holds each
subcommand's output to those words.

## What it needs

git, and `rustc` on `PATH` for `toolchain`. The pack is current as of Rust
1.99, Cargo 1.99 and clippy's lint groups as the rust-clippy README lists them
on 2026-10-13.
