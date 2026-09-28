---
id: TSK-2510
artifact: task
status: approved
revised: 2026-09-28
epic: EPC-1570
closes: [REQ-1186]
issue: 605
projected: c285b90a2fb3
---

# Bind `format` and `lint` to the crate

This repository's `format` and `lint` verbs reach `crates/meow`, so all five
verbs check the crate and the evidence they keep closes REQ-1186, as
ADR-1610's fourth change decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given this change's tree, when `plugins/meow-verbs/bin/meow-verbs run
format lint check test build` runs, then it records five results, each
   with a non-empty command and a pass, `format` ending with `mise run
crate-fmt` and `lint` ending with `mise run crate-lint`. Closed by: the kept
   evidence of that run, citing REQ-1186.
2. Given this change's tree, when `plugins/meow-mise/bin/meow-mise check`
   runs, then it reports 0 findings over task runs that include
   `crate-fmt`, `crate-lint`, `crate-check`, `crate` and `build`. Closed by:
   its output in the pull request.
3. Given a line in `crates/meow/src` left unformatted on purpose, when
   `meow-verbs run format` runs, then it exits 1. Closed by: the kept
   evidence of that failing run, seen once and then reverted.
4. Given a collapsible `if` planted in `crates/meow/src`, when `meow-verbs
run lint` runs, then it exits 1 naming `collapsible_if`. Closed by: the
   kept evidence of that failing run, seen once and then reverted.
5. Given a line in `crates/meow/src` left unformatted on purpose, when `mise
run fmt` runs, then the line takes the formatter's form and `mise run
fmt-check` then exits 0. Closed by: the commands' output in the pull
   request.
6. Given this change, when CI runs it, then `mise run all` passes with
   `crate-fmt`, `crate-lint` and `crate-check` in it, and the pull request
   doesn't merge before that. Closed by: the pull request's CI run.
7. Given this change's tree, when `mise run crate-lint` runs on a clean
   target directory, then its wall time is recorded. Closed by: the timed
   run in the pull request, which ADR-1610 asks for because RES-0278 had only
   a lower bound.

## What to do

Add two tasks to `mise.toml`, and add both to the `depends` of `all`:

- `crate-fmt` runs `cargo fmt --manifest-path crates/meow/Cargo.toml
--check`.
- `crate-lint` runs `cargo clippy --quiet --manifest-path
crates/meow/Cargo.toml --all-features --all-targets -- -D warnings`.

Make the `fmt` task also run `cargo fmt --manifest-path
crates/meow/Cargo.toml`. In `.meowpaw/profile.toml`, append `&& mise run
crate-fmt` to `format` and `&& mise run crate-lint` to `lint`. Keep `-D
warnings` on the command line and add no `[lints]` table to the manifest,
because ADR-1610 keeps a warning from stopping `cargo build`.

If CI's toolchain lacks `rustfmt` or `clippy`, declare both components for
the pinned toolchain in `mise.toml` in this change, because RES-0278 couldn't
see the runner's components.

No unit's shipped behaviour changes, so no unit's version moves.

## Depends on

TSK-2480, because this task edits the profile and `mise.toml` lines that task
writes. TSK-2490 and TSK-2500, because a verb bound to the formatter or to
clippy before the crate passes them fails every pull request.

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

SPC-1080, which already states the five bindings. Each feature linted alone,
a supply-chain check and lint policy beyond clippy's default set, which
ADR-1610 leaves open.
