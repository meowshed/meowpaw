---
id: SPC-1310
artifact: spec
status: live
revised: 2026-10-13
states:
  [
    REQ-2332,
    REQ-0133,
    REQ-3048,
    REQ-2410,
    REQ-2412,
    REQ-2420,
    REQ-2428,
    REQ-2432,
    REQ-2434,
    REQ-2442,
    REQ-2450,
  ]
---

# The Rust pack

## Scope

This covers `meow-rust`, the language pack for Rust. It states what `status`
detects and lists, what `bind` prints, what `check` finds, what `toolchain`
compares, and what the skill and `reviewing.md` carry.

Every rule SPC-1190 states for a language pack holds here, and this document
states only what is Rust's. It leaves supply-chain checks, coverage, unused
dependencies, API compatibility and the slow correctness tools unbound,
because none of them is one of the five stages (RES-0101). Running a stage is
SPC-1040's.

ADR-2660 orders the packs, and ADR-2670 adds the rules every pack keeps.

## Boundary

| Surface                                      | What it is                                                     |
| -------------------------------------------- | -------------------------------------------------------------- |
| `plugins/meow-rust/bin/meow-rust`            | The program: `status`, `bind`, `check` and `toolchain`         |
| `plugins/meow-rust/skills/rust/SKILL.md`     | The skill                                                      |
| `plugins/meow-rust/skills/rust/reviewing.md` | What a reviewer of Rust needs beyond the commands              |
| `plugins/meow-rust/README.md`                | The unit's page                                                |
| `.meowpaw/profile.toml`, `[rust]`            | The pack's settings table, which declares no key yet           |
| Each tracked `Cargo.toml`                    | The marker, and where `bind` and `check` read the lint policy  |
| `rust-toolchain`, `rust-toolchain.toml`      | The pinned toolchain                                           |
| `.config/nextest.toml`                       | What shows the repository runs its tests through cargo-nextest |

The program is the `rust` feature of `crates/meow`, built by `build-units`.
`status`, `bind` and `check` run git alone, as SPC-1190 states. `toolchain`
runs `rustc --version`, and nothing else.

The pack was observed against Rust 1.99, Cargo 1.99 and cargo-nextest's
documentation as RES-0101 read it (RES-0101, RES-0361).

## Behaviour

### Detection

A work tree holds Rust where git tracks a `Cargo.toml`, wherever it lies
(REQ-2332, REQ-0133). `status` reports once for each directory holding one,
naming the directory and the part that holds it (REQ-3048).

The workspace is the set of manifests under one top manifest: a tracked
`Cargo.toml` with no other tracked `Cargo.toml` in a directory above it.
`bind` binds one workspace. Where git tracks two or more top manifests,
every stage is printed `# <stage>: unresolved, several Cargo manifests outside
one workspace: <files>`, because no one cargo command reaches them all.

### What `status` reports

In this order:

1. For each directory holding a `Cargo.toml`, the scope line, `marker:
<file>`, and `edition: <edition>`, or `edition: none declared, so cargo
compiles it as the 2015 edition` (RES-0101). A manifest with a
   `[workspace]` table adds `workspace: <file> declares one`.
2. `lockfile: Cargo.lock tracked`, or `lockfile: none tracked`.
3. `toolchain: <file> pins <channel>`, or `toolchain: nothing pinned`.
4. `clippy groups: <groups>`, the groups the top manifest's lint policy
   enables, as `check` names them below (REQ-2432).
5. `nextest: .config/nextest.toml` where git tracks that file.

### What `bind` prints

The top manifest decides each stage's words. Where it isn't at the root, each
command names it with `--manifest-path <file>`. Where it holds a `[workspace]`
table, each command but `format` takes `--workspace`, and `format` takes
`--all`. Where any tracked manifest in the workspace declares `[features]`,
`lint`, `check`, `test` and `build` take `--all-features`, so code behind a
feature that isn't on by default compiles in some stage. No stage checks a
combination of features short of all of them (RES-0101).

| Stage    | Printed as                                              | When                             |
| -------- | ------------------------------------------------------- | -------------------------------- |
| `format` | `cargo fmt --check`                                     | Always                           |
| `lint`   | `cargo clippy --all-targets -- -D warnings`             | Always                           |
| `check`  | `cargo check --all-targets`                             | Always                           |
| `test`   | `cargo nextest run`, then `cargo test --doc` with a lib | A tracked `.config/nextest.toml` |
| `test`   | `cargo test`                                            | No nextest configuration         |
| `build`  | `cargo build`                                           | Always                           |

rustfmt, clippy and cargo ship with rustup, and the manifest is the
configuration that names them, so `format`, `lint`, `check` and `build` bind
from the manifest alone (RES-0101). `-D warnings` turns on no lint: it fails
the stage on the warnings the configured groups already report.
`--all-targets` puts tests, examples and benchmarks under the lint policy.

`test` binds cargo-nextest only where `.config/nextest.toml` shows the
repository configured it, and `cargo test` otherwise, never choosing between
them by what is installed (REQ-2420). cargo-nextest runs no doctests, so where
a library target exists, a tracked `src/lib.rs` or a `[lib]` table, the stage
runs `cargo test --doc` after it, with the same manifest, workspace and
feature words (REQ-2412, RES-0361). A crate with no library target has no
doctests, and its `test` stays `cargo nextest run`. A runner that leaves out
the documentation examples never binds: the stage is printed unresolved
naming them. Under `lint`, a comment names the clippy groups the stage runs
(REQ-2432).

Where a toolchain file pins a version, a comment names it and says rustup runs
each stage under it, and that `meow-rust toolchain` compares it with the one
installed (REQ-2428). A `mise.toml` or a `Taskfile.yml` is named with the
runner's pack, as SPC-1195 states for Markdown. A stage the profile already
declares is left out, and `bind` exits 0 once it prints the table.

### What `check` finds

`check` exits 1 on any finding, each naming the file (REQ-2434):

| Finding                                                                                                                                 | When                                                                                                                    |
| --------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `<file>: no edition, so cargo compiles it as the 2015 edition`                                                                          | A `[package]` table declares no `edition`                                                                               |
| `<file> doesn't inherit the workspace's lints: set workspace = true under [lints]`                                                      | The top manifest declares `[workspace.lints]`, and a member's `[package]` manifest doesn't set `lints.workspace = true` |
| `<target> isn't ignored, and cargo writes its build output there`, where `<target>` is `target`, or `<directory>/target` below the root | No ignore file the repository tracks covers `target` beside the top manifest (REQ-2442)                                 |

Cargo writes its build output to `target/` at the workspace's root unless
`CARGO_TARGET_DIR` or `build.target-dir` moves it (RES-0361), so the stages
`bind` prints leave nothing a repository that ignores `target/` sees in its
working tree. A global excludes file and `.git/info/exclude` protect one clone
only, so neither counts.

With no finding, `check` prints `no findings; rule groups enabled:` followed by
the three settings it checked, and then `clippy groups: <groups>`.

### The clippy groups a stage runs

A clean `lint` is clean against `correctness`, `suspicious`, `style`,
`complexity` and `perf`, which clippy turns on by default (RES-0361). A group
the top manifest's `[lints.clippy]` table, or its `[workspace.lints.clippy]`
table, sets to `warn`, `deny` or `forbid` joins them, and one it sets to
`allow` leaves. A lint's level is a string or a table with a `level` key. The
pack turns on no group itself (REQ-2422 through SPC-1190).

### What `toolchain` compares

`meow-rust toolchain` reads the pinned toolchain: the `channel` of the
`rust-toolchain` or `rust-toolchain.toml` file nearest the top manifest, the
first where both exist, or the whole first line of a `rust-toolchain` that
isn't TOML (RES-0361). It runs `rustc --version` in the top manifest's
directory, where rustup's proxy runs the toolchain the file selects, and
compares its version with the pin, to the pin's precision (REQ-2428):

| State                                                  | Printed as                                                   | Exit |
| ------------------------------------------------------ | ------------------------------------------------------------ | ---- |
| No toolchain file                                      | `toolchain: nothing pinned`                                  | 0    |
| A channel such as `stable` or `nightly`                | `toolchain: <file> pins the <channel> channel, no version`   | 0    |
| The installed version matches                          | `toolchain: rust <pin>, pinned in <file> and installed`      | 0    |
| The installed version differs                          | `unresolved: rust <pin> pinned, <version> installed`         | 3    |
| `rustc` exits non-zero, such as on a missing toolchain | `unresolved: rust <pin> pinned, none installed` and its line | 3    |
| `rustc` isn't on `PATH`                                | `tool absent: rustc`                                         | 3    |
| `rustc` prints no version                              | `tool broken: rustc printed <first line>`                    | 3    |

### Generated files

`Cargo.toml`, `Cargo.lock`, the toolchain file, `.config/nextest.toml` and any
`rustfmt.toml` or `clippy.toml` are project state to commit (RES-0101).
`target/` is cache to ignore (REQ-2450). The README states both.

### What the skill carries

The skill's body gives, in order: detection, the stages and what `bind` prints
for each, the doctest rule, what to read before reporting a pass, and the
prohibitions. It forbids enabling `pedantic` wholesale, writing `#![deny]`
into source, binding `test` to cargo-nextest alone, and reporting a licence or
advisory finding as a lint (RES-0101).

`reviewing.md` carries what a Rust reviewer checks that no command reports:
ownership as a design choice, the error boundary, `unwrap` and `expect`
outside tests, feature combinations, the invariant beside each `unsafe`
block, and the public surface (RES-0101).

## Failure paths

Each is printed as SPC-1190 states, by every command it applies to:

| State                                       | Reported as                                                                                | Exit |
| ------------------------------------------- | ------------------------------------------------------------------------------------------ | ---- |
| Git tracks no `Cargo.toml`                  | `unresolved: not a Rust repository`                                                        | 3    |
| No profile, or a profile that doesn't parse | `unresolved: <what is wrong with the profile>`                                             | 3    |
| Two or more top manifests                   | each stage `# <stage>: unresolved, several Cargo manifests outside one workspace: <files>` | 0    |
| A manifest that doesn't parse               | `unresolved: <file> doesn't parse as TOML: <message>`                                      | 3    |
| `toolchain`: as its table states            | as its table states                                                                        | 3    |
