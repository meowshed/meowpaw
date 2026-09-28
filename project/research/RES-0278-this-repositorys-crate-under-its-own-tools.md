---
id: RES-0278
artifact: research
status: approved
revised: 2026-09-28
elaborates: RES-0101, RES-0023
---

# This repository's crate fails two of Rust's own checks, and no verb runs any of them

## Summary

The native tool every unit ships, `crates/meow`, passes the compiler and its
18 tests, and fails Rust's formatter and linter. On 2026-09-28, on `main` as
pull request #595 left it, `cargo fmt --check` found 464 places in all 14
source files whose layout differs from the formatter's, and `cargo clippy` with
warnings denied stopped on 15 errors in three files. Neither failure shows
anywhere, because this repository's profile binds `format`, `lint` and `test`
to checks of Markdown, prompts and Python fixtures, and leaves `check` and
`build` undeclared. The crate's tests run only in the gate's `crate` task,
which no verb names. A verb bound today to the formatter or to the linter with
warnings denied fails on its first run. Denying warnings also ties `lint` to
the Rust pin, because clippy's default set changed in each of the last three
releases.

This covers what the Rust tools on this machine do to this crate. It adds
observations to RES-0101, which read the tools' documentation and ran none of
them. It doesn't cover another repository's crate or any tool outside the
rustup distribution.

## The question

RES-0023 concluded that helpers are covered by the same verification verbs as
any other code the harness ships. The helpers are the `meow` binary built from
`crates/meow`, so the question is what each Rust tool reports on that crate
today, how long it takes, and whether a verb bound to it would pass on its
first run.

## Method

I ran the tools on 2026-09-28 in a worktree of `main` as #595 left it, through
`mise exec`, which selects the toolchain `mise.toml` pins. The versions were
cargo 1.98.1, rustc 1.98.1, rustfmt 1.9.0 and clippy 0.1.98. I read the
profile with `meow-verbs status` and the gate's tasks with `meow-mise check`
and `meow-mise bind`. I timed runs with `/usr/bin/time -p` and give the wall
time, on an Apple silicon laptop.

To see what a `[lints]` table does to a build, and to time a cold
`build-units`, I copied the crate's manifest, lock file, sources and
`build-units` into a scratch directory and built the copy into its own target
directory. To see what `cargo fmt` and `cargo clippy --fix` change, I
extracted the tree with `git archive` into two more scratch directories, each
its own git repository, because one of the crate's tests scans the
repository's files and fails in a copy of the crate alone. The crate in the
repository was not changed.

I didn't run anything in CI. The last CI run on `main`, 36435654220, shows mise
finding Rust 1.98 already installed on the runner, and its log doesn't say
whether the runner's toolchain carries `rustfmt` and `clippy`.

## Findings

### The profile binds no verb to the crate

`meow-verbs status` reports `format` as `mise run fmt-check`, which runs
Prettier on Markdown, and `lint` as eight commands over Markdown, output
styles, prompts, unit boundaries, budgets, licences and the mise bindings.
`test` builds the units and runs the Python fixtures and the record's checks.
`check` and `build` are unresolved as undeclared, and the profile's comment
says the repository has neither.

The crate's own tests run from the `crate` task in `mise.toml`, `cargo test
--all-features`, which the gate's `all` task depends on. No verb names that
task, so `meow-verbs run test` never runs them, and evidence kept from the
verbs says nothing about the crate.

`meow-mise bind` offers `lint` and `build`, from tasks of those names, and
finds no task named `format`, `check` or `test`. `meow-mise check` reports 0
findings in the 7 task runs the profile names.

### The crate's tests pass

`mise run crate` exited 0 and printed `test result: ok. 18 passed; 0 failed; 0
ignored`. The run took 3.2 seconds of wall time, of which the tests took 0.05
seconds and compiling took the rest. The target directory was as earlier runs
that day had left it. The same `cargo test --all-features` into an empty target
directory exited 0 with the same result and took 3.4 seconds of wall time, so
a cold run costs about as much as a warm one.

### `build-units` passes, in 80 seconds cold and under a second warm

`crates/meow/build-units` in the scratch copy, into empty target directories,
exited 0, printed `built <unit>` for each of the nine units, and took 79.8
seconds of wall time and 136.6 seconds of CPU time. It builds nine release
binaries, one for each feature, each into its own target directory, so
nothing compiled for one unit is reused by the next. Run again with nothing
changed, it exited 0 in 0.35 seconds. `mise run build` in the worktree, whose
units were already built, exited 0 in 0.48 seconds.

### The formatter finds 464 differences, and the crate has no formatter configuration

`cargo fmt --manifest-path crates/meow/Cargo.toml --check` exited 1 and
printed 464 `Diff in` blocks, spread over all 14 source files: 176 in
`record.rs`, 41 in `verbs.rs`, 38 in `verbs/ledger.rs`, 35 in `mise.rs`, 30
in `gotask.rs`, and between 2 and 26 in each of the other nine. The first is a
chained call on one line that the formatter splits across several. The check
took 0.2 seconds of wall time, because the formatter compiles nothing.

The repository holds no `rustfmt.toml`, `.rustfmt.toml` or
`rust-toolchain.toml`, so the formatter applies its defaults for the
manifest's 2024 edition.

### The formatter changes more than whitespace, and the tests still pass

In a scratch copy, `cargo fmt` exited 0 and changed all 14 files, 3,178 lines
added and 715 removed. `cargo fmt --check` then exited 0, and `cargo test
--all-features` exited 0 with 18 passed. Comparing each file before and after
with every whitespace character and comma removed, 13 of the 14 files still
differ, and only `runner.rs` changed in whitespace alone. The rest of the
difference has two shapes. The formatter moves 58 match arm bodies into a new
block, and a `return` moved that way gains a `;`. It also sorts `mod`
declarations and the names inside a `use`, which accounts for 22 added or
removed lines. I found no source stating that the formatter never
changes what the code does, so the check a reformat has is the one above: the
formatter's own check passes afterwards, and so do the tests.

### `cargo clippy --fix` fixes 13 of the 15 findings

In a second scratch copy, `cargo clippy --fix --allow-dirty --all-features
--all-targets` exited 0 and reported 1 fix in `author.rs`, 1 in `git.rs` and
11 in `record.rs`, a diff of 25 lines added and 37 removed over the three
files. The same clippy command with `-D warnings` then exited 101 on the two
it left, `skip_while_next` and `regex_creation_in_loops`, and `cargo test
--all-features` exited 0 with 18 passed. So the ten `collapsible_if`, the two
`collapsible_match` and the `manual_repeat_n` have a mechanical fix, and two
findings need an edit a person writes.

### The linter stops on 15 errors in three files

`cargo clippy --manifest-path crates/meow/Cargo.toml --all-features
--all-targets -- -D warnings` exited 101 and reported 15 errors in the binary
and the same 15 in its tests: 13 in `record.rs`, one in `author.rs` and one in
`git.rs`. Ten are `collapsible_if`, two are `collapsible_match`, and
`manual_repeat_n`, `regex_creation_in_loops` and `skip_while_next` fire once
each. The manifest has no `[lints]` table, so every one comes from clippy's
default set.

A cold run into an empty target directory took 2.4 seconds of wall time. That
figure is a lower bound, because clippy stopped at the errors. I didn't time a
clean crate, because none exists yet.

The same command without `-D warnings` exited 0 and printed the same 15
findings as warnings, so a `lint` verb bound to it passes whatever clippy
finds.

### Clippy's default set changed in each of the last three releases

Clippy's changelog lists, for each Rust release, the lints it adds and the
lints it moves between groups. The default set is the lints in the
`correctness`, `suspicious`, `style`, `complexity` and `perf` groups. I read
the changelog through a fetch tool that summarises the page, so the counts
below are as that tool quoted them. Rust 1.96 added three lints to `complexity`. Rust 1.97 added two to `perf` and
moved `nonminimal_bool` and `overly_complex_bool_expr` out of the default set
into `pedantic`. Rust 1.98 added five: two to `complexity`, one to `style` and
two to `suspicious`.

So a run with `-D warnings` can fail on a change that moves the Rust pin in
`mise.toml`, with no change to the crate. `mise.toml` pins `rust = "1.98"`,
a prefix that mise resolved to 1.98.1. A later 1.98 patch release could
therefore arrive without an edit to the pin, and a new minor release, the kind
the changelog lists lints for, arrives only in a change that edits it.

### A `[lints.clippy]` table doesn't reach a build, and a `[lints.rust]` table does

In the scratch copy, a `[lints.clippy]` table setting `all` to `deny` left
`cargo build --all-features --all-targets` exiting 0 with no output, and made
`cargo clippy --all-features --all-targets` exit 101 on the same 15 findings,
now as errors. Cargo applies that table's lints only when clippy runs.

In the other scratch copy, a `[lints.rust]` table setting `warnings` to `deny`
made `cargo build --no-default-features` exit 101 on `error: unused variable:
rest`, the warning described below, and left `cargo build
--no-default-features --features verbs` exiting 0. The compiler applies that
table on every build, so a warning in the code being built stops the build.

### The compiler finds nothing with every feature on, and one warning with none

`cargo check --all-features --all-targets` exited 0 with no warning, and its
cold run took 2.4 seconds. `build-units` builds each unit with
`--no-default-features` and one feature, and the manifest declares nine:
`verbs`, `scm`, `git`, `record`, `github`, `licence`, `author`, `mise` and
`gotask`. `cargo check --no-default-features --features <feature>
--all-targets`, run once for each of the nine, exited 0 with 0 warnings every
time. With no feature at all it exited 0 with one warning, an unused variable
`rest` in `main.rs`. No unit is built without a feature, so no shipped binary
carries that warning.

### The pinned toolchain carries both tools on this machine

`rustup component list --installed` under the `1.98.1` toolchain lists
`clippy` and `rustfmt`. An earlier query for the channel `1.98` made rustup
install a second toolchain of that name. It doesn't affect runs through
`mise exec`, because mise sets `RUSTUP_TOOLCHAIN=1.98.1`, and `rustup show
active-toolchain` under `mise exec` names `1.98.1`.

## Conclusions

1. A verb bound to `cargo fmt --check` fails on its first run until the crate
   is reformatted, and one bound to `cargo clippy -D warnings` fails until the
   15 lint findings are fixed.
2. Reformatting touches all 14 source files and changes more than layout: it
   sorts `mod` and `use` declarations and moves 58 match arm bodies into
   blocks. No
   source found says that it never changes behaviour, so what confirms a
   reformat is `cargo fmt --check` exiting 0 and the 18 tests passing after
   it. `cargo clippy --fix` fixes 13 of the 15 lint findings with the tests
   still passing, and two need an edit a person writes and reviews.
3. `cargo check --all-features --all-targets` passes today with no warning,
   and so does each of the nine features `build-units` ships, checked alone.
   A run with every feature on doesn't check each feature alone, so a warning
   that only one feature alone produces would pass it. The no-feature warning
   is outside what ships.
4. The crate's 18 tests pass through the gate's `crate` task, and `mise run
build` exits 0, so `check`, `test` and `build` each have a command that
   passes today.
5. Denying warnings ties the `lint` verb's result to the Rust pin as well as
   to the crate: clippy's default set changed in each of 1.96, 1.97 and 1.98,
   so moving the pin can fail `lint` on code nobody touched. Two alternatives
   exist. A `[lints.clippy]` table keeps the policy in the manifest and
   leaves builds alone, but keeps the same tie to the pin. A run without
   `-D warnings` removes the tie and the failure together, so `lint` passes
   with findings open.
6. On this machine the formatter's check costs 0.2 seconds, clippy at least
   2.4 seconds cold, a lower bound because it stopped at its errors, `cargo
check` 2.4 seconds cold, and the tests 3.2 seconds warm and 3.4 cold. A
   cold `build-units` costs 80 seconds, and a warm one under a second. The
   `test` verb already runs `build-units` first, so a `build` verb run after
   it pays the warm cost. The verbs gain seconds, except where the target
   directories start empty, as on a fresh checkout, where `build-units`
   alone costs over a minute.
7. Whether CI's toolchain carries `rustfmt` and `clippy` is unobserved, so the
   first CI run with the new tasks is what shows it.

## Sources

- `crates/meow` as #595 left it, read and run 2026-09-28, through cargo 1.98.1,
  rustfmt 1.9.0 and clippy 0.1.98 - every count and time above, including
  those from the three scratch copies.
- `crates/meow/Cargo.toml`, read 2026-09-28 - the nine features and the absence
  of a `[lints]` table.
- `crates/meow/build-units`, read 2026-09-28 - each unit built with
  `--no-default-features` and one feature.
- `.meowpaw/profile.toml` and `mise.toml` as #595 left them, read 2026-09-28 -
  what each verb and the gate run, and the Rust pin.
- `meow-verbs status`, `meow-mise check` and `meow-mise bind`, run 2026-09-28 -
  the verbs as resolved and the tasks a verb could bind to.
- CI run 36435654220 on `main`, read 2026-09-28 - Rust 1.98 already present on
  the runner.
- [Clippy's changelog](https://github.com/rust-lang/rust-clippy/blob/master/CHANGELOG.md), read 2026-09-28 -
  the lints added and moved in Rust 1.96, 1.97 and 1.98, as a summarising
  fetch tool quoted them.
- RES-0023, read 2026-09-28 - helpers covered by the same verbs as any other
  code.
- RES-0101, read 2026-09-28 - the mapping from each verb to a Rust tool, read
  from the vendor documentation.
