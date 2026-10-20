---
reader: someone choosing or running meow-rust
answers: what meow-rust does, what it adds to a session and how to run it
kind: reference
describes: [meow-rust@0.1.0]
---

# meow-rust

`meow-rust` tells you whether your repository holds Rust, lists each manifest's
edition and the toolchain you pinned, prints a `[stages]` table bound from the
cargo commands your manifests call for, checks the settings behind your
stages, and compares your pinned toolchain with the installed one. Its skill
tells Claude Code what a reviewer of Rust checks that no command reports.
`status`, `bind` and `check` read the files git tracks and run git alone;
`toolchain` runs `rustc --version`. It writes no file, and it installs on its
own, with no other part of the `meowpaw` harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://paw.retran.me/meowpaw/marketplace.json
claude plugin install meow-rust@meowpaw
```

Installing this unit also enables `meow-core`, which ships the shared `paw` binary its launcher runs, and the platform keeps `meow-core` enabled while this unit is on, so you can't disable `meow-core` alone.

Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions, because the unit's behaviour was never seen on an older one.

## Run it

Claude Code puts the unit's `bin/` directory on its Bash tool's `PATH`, so
Claude Code runs it in your repository as:

```bash
meow-rust status
```

From your own shell, run the same launcher by its path in the installed unit.

The program counts a repository as Rust where git tracks a `Cargo.toml`,
wherever it lies. `status` prints, for each directory holding one, a
`scope: <directory>` line, or `scope: <part> <directory>` where your profile's
`[parts]` declares a part holding it, then:

1. `marker: <file>`.
2. `edition: <edition>`, or `edition: none declared, so cargo compiles it as the
2015 edition`.
3. `workspace: <file> declares one`, where the manifest has a `[workspace]` table.

After the directories it prints `lockfile:`, `toolchain:` for the file that
pins one, `clippy groups:` for the groups your `lint` stage runs, and
`nextest:` where git tracks `.config/nextest.toml`.

Every command that reads the profile first prints its state, `profile: absent`,
`profile: unparseable` or `profile: parsed`, and `unknown key: <path>` for each
key no unit reads. `bind` prints them on standard error, so what it prints on
standard output stays ready to paste.

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
and any `rustfmt.toml` or `clippy.toml`, because each is project state: without
them a collaborator builds with other dependencies, another toolchain or other
settings. Ignore `target/`, the cache cargo writes at the workspace's root
unless `CARGO_TARGET_DIR` or `build.target-dir` moves it, because it is
regenerated on the next build and fills the history with noise. `check` reports
a `target` no ignore file covers.

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

When Claude Code reviews Rust, the skill has it run `status` first, and then
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

Claude Code 2.1.280 or later, declared in
`plugins/meow-rust/requires.toml`, and git. `toolchain` needs `rustc` on
`PATH`. The pack is current as of Rust 1.99, Cargo 1.99 and clippy's lint groups
as the rust-clippy README lists them on 2026-10-13. cargo-nextest and the other
tools in the Rust toolchain are named, never required: the pack binds one only
where your repository configured it.
