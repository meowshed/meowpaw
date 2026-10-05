---
id: ADR-1610
artifact: adr
status: done
revised: 2026-09-28
addresses: [REQ-1186]
postpones: []
supersedes: []
---

# 1610. This repository binds its five verbs to the crate's own tools, after the crate passes them

## Decision

This repository's profile binds each of the five verbs to the Rust tool that
answers it for `crates/meow`, alongside what each verb already runs, so the
native tool every unit ships passes the same verbs as the Markdown, prompts
and fixtures beside it (REQ-1186). `mise.toml` gains three tasks, and the
gate's `all` task depends on each of them:

| Task          | Runs                                                                                                      |
| ------------- | --------------------------------------------------------------------------------------------------------- |
| `crate-fmt`   | `cargo fmt --manifest-path crates/meow/Cargo.toml --check`                                                |
| `crate-lint`  | `cargo clippy --quiet --manifest-path crates/meow/Cargo.toml --all-features --all-targets -- -D warnings` |
| `crate-check` | `cargo check --quiet --manifest-path crates/meow/Cargo.toml --all-features --all-targets`                 |

The profile's verbs then read:

| Verb     | Adds, or becomes                                                                                 |
| -------- | ------------------------------------------------------------------------------------------------ |
| `format` | adds `mise run crate-fmt` after `mise run fmt-check`                                             |
| `lint`   | adds `mise run crate-lint` after the eight commands it runs today                                |
| `check`  | becomes `mise run crate-check`, where today it is undeclared                                     |
| `test`   | adds `mise run crate`, the existing `cargo test --all-features`, after `crates/meow/build-units` |
| `build`  | becomes `mise run build`, which runs `crates/meow/build-units`, where today it is undeclared     |

The profile's comment saying the repository has neither `check` nor `build`
goes, because after this decision it has both. The `fmt` task, which writes,
gains `cargo fmt` on the crate in the fourth change below, so a person who
fixes a `format` failure runs one command for both kinds of file.

A verb is bound only to a command that passes, because a verb that fails on
its first run blocks every pull request until somebody fixes code the pull
request didn't touch. RES-0278 found that `check`, `test` and `build` each have
a passing command today, `mise run build` among them, and that `cargo fmt --check` reports 464 differences
over all 14 source files and clippy stops on 15 errors in three files. So the
work lands as four changes in this order:

1. `crate-check` and its `all` dependency land, and `check`, `test` and
   `build` are bound, so two unresolved verbs resolve a step before the crate
   is cleaned.
2. The crate is reformatted by `cargo fmt` and nothing else. RES-0278 found
   that the formatter sorts declarations and moves match arm bodies into
   blocks as well as changing layout, so the change shows `cargo fmt --check`
   exiting 0 and the crate's 18 tests passing after it.
3. The 15 lint findings are fixed, with the crate's tests passing before and
   after. RES-0278 found that `cargo clippy --fix` fixes 13 of them, so that
   part lands as its own commit, and the two it leaves,
   `skip_while_next` and `regex_creation_in_loops`, are edited by hand.
4. `crate-fmt`, `crate-lint`, their `all` dependencies, `cargo fmt` in the
   `fmt` task and the `format` and `lint` bindings land together, with the
   evidence that closes REQ-1186.

Each change leaves the gate green, because nothing checks the crate's format
or lints until the fourth one lands.

`-D warnings` stays on the command line of `crate-lint`, and the manifest
gains no `[lints]` table. The command line makes a warning fail the gate and
leaves `cargo build` and `build-units` compiling a crate with a warning, so a
person mid-change still gets a binary to run.

After this decision, `meow-verbs run format lint check test build` in this
repository runs the crate's formatter, linter, type check, tests and build,
none of the five is unresolved, and evidence kept from the verbs covers the
crate. What still doesn't work:

- A shipped binary is built with one feature, and the lint and the type check
  run with every feature on. RES-0278 found each feature alone clean on
  2026-09-28, and nothing keeps it so: a warning that appears with one
  feature alone, such as an import only another feature uses, passes the
  verbs.
- Whether CI's toolchain carries `rustfmt` and `clippy` is unobserved until
  the fourth change's first CI run.
- The crate's dependencies aren't audited, and no verb runs a supply-chain
  check, which RES-0101 places outside the five verbs.

## Why

REQ-1186 asks for the same verbs, and RES-0278 shows that none of them reaches
the crate today: `format`, `lint` and `test` run checks of other files, and
`check` and `build` are undeclared. The crate's tests run only from the gate's
`crate` task, so evidence the verbs keep says nothing about the code every unit
executes. REQ-1673 asks the harness to verify its own repository through its
own verbs, and a harness whose one compiled program sits outside them hasn't
shown that.

RES-0101 gives the mapping: `rustfmt` for `format`, clippy with every target
and warnings denied for `lint`, `cargo check` for `check`, `cargo test` for
`test`, and a build for `build`. It says `--all-targets` puts the tests under
the same lint policy as the binary, and that `cargo test` runs doctests where
the faster runner doesn't. The crate is a binary with no doctests, so
`cargo test` loses nothing either way, and it is already what the gate runs.

The tasks sit in `mise.toml`, and the profile names them through `mise run`,
because ADR-1580's `meow-mise check` reads the task runs the profile names,
and a verb bound to a task shows up in its report. A cargo command written into
the profile directly would pass `meow-mise check` unseen.

The strongest objection is that `-D warnings` makes the gate fail on a lint
that a new clippy adds, with no change to the crate. RES-0278 found clippy's
default set changed in each of Rust 1.96, 1.97 and 1.98. `mise.toml` pins the
prefix `1.98`, so a new minor release, the kind that brings new lints, arrives
only in a change that edits the pin, and that change is where its findings get
fixed. A run without `-D warnings` removes that cost and also removes the
failure: RES-0278 saw clippy exit 0 with all 15 findings open, so `lint` would
pass whatever clippy says.

## Alternatives

| Option                                                                                                            | Better at                                                                    | Why it lost                                                                                                                             |
| ----------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Bind the verbs first, and fix the crate in the same change                                                        | One change, one review                                                       | A 464-place reformat and 15 hand fixes in one diff leave the mechanical part unreadable beside the edited part                          |
| Put `warnings = "deny"` in a `[lints.rust]` table in the manifest                                                 | Policy in the manifest, where RES-0101 says it belongs                       | RES-0278 saw such a table fail `cargo build` on one warning, so `build-units` would refuse to build a crate mid-change                  |
| Deny clippy's set in `[lints.clippy]`, and keep `-D warnings` on the command line for the compiler's own warnings | Clippy's policy in the manifest, and builds unaffected, as RES-0278 observed | The policy splits over two files, and a reader of either sees half of it; the command line holds all of it in the one task that runs it |
| Run clippy without `-D warnings`                                                                                  | No failure when the Rust pin moves                                           | RES-0278 saw it exit 0 with 15 findings open, so `lint` would pass whatever clippy finds                                                |
| Bind all five verbs in the last change                                                                            | One change touches the profile, not two                                      | `check`, `test` and `build` pass today, so holding them back leaves two verbs unresolved for no reason                                  |
| Write the cargo commands into the profile, with no `mise.toml` task                                               | One file changes, not two                                                    | `meow-mise check` reads only the task runs the profile names, and the gate's `all` would not run the same commands                      |
| Lint and check each feature alone, nine runs of each                                                              | Catches a warning only one shipped feature produces                          | Nine runs where one finds today what nine do, for a gap RES-0278 found empty                                                            |
| Do nothing                                                                                                        | No change to the gate                                                        | REQ-1186 stays unmet, and two of the five verbs stay unresolved in the repository that ships them                                       |

## What it costs

Whoever runs the gate or the verbs waits for clippy and `cargo check` over the
crate. RES-0278 measured each at 2.4 seconds cold on this machine, and clippy
stopped at its errors there, so a clean crate might take longer; the fourth
change measures that and records it in its evidence. `lint` today compiles the
crate with the `author` feature alone, for `prompts` and `budget`, into
`target/author`. The gate's `crate` task already builds the crate's tests with
every feature into its default target directory, `crates/meow/target`.
`crate-lint` and `crate-check` add clippy's and the type check's output for
every target to that tree, so it grows, and no new tree appears. The `build`
verb runs `build-units`, which `test` already runs first, so a `build` run
after `test` costs under a second; RES-0278 timed a cold `build-units` at 80
seconds, which a fresh checkout pays once, through either verb.

Whoever changes the crate formats it and keeps clippy quiet on every change,
and whoever moves the Rust pin fixes the lints the new clippy adds in that
change. The reformat conflicts with every open branch that touches
`crates/meow`, so each such branch rebases once and runs `cargo fmt`.

A premortem, written as though it had failed: the fourth change merged, and a
week later every pull request failed `lint` in CI with `no such command:
clippy`, because the runner's toolchain lacked the component and nobody had
seen CI run the task before it merged. The fourth change's own CI run is the
check that rules this out, so it doesn't merge until CI has run `crate-lint`
and `crate-fmt` and both passed. Where the components are missing, that
change declares them for the pinned toolchain in `mise.toml`.

## What would reverse it

- I would move clippy's policy into a `[lints.clippy]` table if a second
  command besides `crate-lint` came to run clippy on this crate, because it
  would then have to repeat the task's flags.
- I would lint each feature alone if a warning reached a shipped binary that
  the run with every feature missed.
- I would drop `-D warnings`, and write the policy lint by lint instead, if
  moving the pin to a new minor release brought clippy findings that couldn't
  be fixed in the change that moves the pin, because the pin would then have
  to wait for the crate, and the tie this decision accepts would be holding
  the toolchain back.

## Consequences

- `mise.toml` gains `crate-fmt`, `crate-lint` and `crate-check`, `all` depends
  on them, and `fmt` also runs `cargo fmt` on the crate.
- `.meowpaw/profile.toml` binds all five verbs, and its comment on `check` and
  `build` goes.
- Every file under `crates/meow/src` is reformatted, and `record.rs`,
  `author.rs` and `git.rs` change to satisfy clippy.
- No unit's shipped behaviour changes, so no unit's version moves.
- SPC-1080, the native tool's specification, states the checks the crate
  passes.

## How I will know it was realised

1. `cargo fmt --manifest-path crates/meow/Cargo.toml --check` and the clippy
   command in `crate-lint` each exit 0 on `main`.
2. `plugins/meow-verbs/bin/meow-verbs run format lint check test build`
   records five results, each with a non-empty command, and `check` and
   `build` no longer read as unresolved.
3. `plugins/meow-mise/bin/meow-mise check` reports 0 findings, over the task
   runs the profile names, which include `crate-fmt`, `crate-lint`,
   `crate-check`, `crate` and `build`.
4. A line in `crates/meow/src` left unformatted on purpose makes
   `meow-verbs run format` exit 1, and a planted clippy finding, such as a
   collapsible `if`, makes `meow-verbs run lint` exit 1. Each is seen once and
   then reverted, and the kept evidence of those runs and of the passing run
   closes REQ-1186.
5. The CI run of the fourth change passes `mise run all` with the three new
   tasks in it.

## What this does not settle

- REQ-1188, which asks for helpers in the one language the plugin platform
  installs dependencies for, while ADR-1110 made them a Rust binary. The two
  disagree, and this decision neither withdraws REQ-1188 nor applies it.
- A supply-chain check of the crate's dependencies.
- How a repository other than this one binds its verbs for Rust, which a Rust
  pack decides for REQ-2332.
- Lint policy beyond clippy's default set.
