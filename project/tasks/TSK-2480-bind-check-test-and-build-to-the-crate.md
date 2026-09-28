---
id: TSK-2480
artifact: task
status: approved
revised: 2026-09-28
epic: EPC-1570
closes: []
issue: 602
projected: 081cc33d99b4
---

# Bind `check`, `test` and `build` to the crate

This repository's `check`, `test` and `build` verbs reach `crates/meow`, the
three whose commands pass on the crate today, as ADR-1610's first change
decides. `check` and `build` stop reading as unresolved. One task, one
branch, one pull request, one review.

## Acceptance criteria

1. Given this change's tree, when `mise run crate-check` runs, then it exits
   0 with no warning. Closed by: the command's exit status and output in the
   pull request.
2. Given this change's tree, when `plugins/meow-verbs/bin/meow-verbs run
check test build` runs, then it records three results, each with a
   non-empty command, `check` running `mise run crate-check`, `test` running
   `mise run crate` after `crates/meow/build-units` and `build` running `mise run build`, and none reads
   as unresolved. Closed by: the kept evidence of that run.
3. Given this change's tree, when `plugins/meow-mise/bin/meow-mise check`
   runs, then it reports 0 findings over task runs that include
   `crate-check`, `crate` and `build`. Closed by: its output in the pull
   request.
4. Given this change's tree, when `mise run all` runs, then `crate-check` is
   among the tasks it runs and it exits 0. Closed by: the gate's output and
   the pull request's CI run.

## What to do

Add a task `crate-check` to `mise.toml` that runs `cargo check --quiet
--manifest-path crates/meow/Cargo.toml --all-features --all-targets`, and add
it to the `depends` of `all`. In `.meowpaw/profile.toml`, set `check` to `mise
run crate-check` and `build` to `mise run build`, and append `&& mise run
crate` to `test` after `crates/meow/build-units`, so the crate's tests run
before the fixtures. Replace the profile's comment that says the repository
has neither `check` nor `build`, because after this change it has both.

Leave `format` and `lint` as they are: the crate fails `cargo fmt --check` and
clippy until TSK-2490 and TSK-2500 land, and a verb bound to either now fails
every pull request.

No unit's shipped behaviour changes, so no unit's version moves.

## Depends on

Nothing. The commands it binds pass on the crate as it stands, which
RES-0278 observed, and it touches no file under `crates/meow`, so it runs in
parallel with TSK-2490.

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

`format` and `lint`, which TSK-2510 binds once the crate passes them.
SPC-1080 already states all five bindings, so it doesn't change. The crate's
source, which this task doesn't touch.
