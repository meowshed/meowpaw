---
id: TSK-2490
artifact: task
status: approved
revised: 2026-09-28
epic: EPC-1570
closes: []
issue:
---

# Reformat the crate with `cargo fmt`

Every file under `crates/meow/src` takes the form `cargo fmt` gives it, and
the change holds nothing else, as ADR-1610's second change decides. One task,
one branch, one pull request, one review.

## Acceptance criteria

1. Given this change's tree, when `cargo fmt --manifest-path
crates/meow/Cargo.toml --check` runs, then it exits 0 with no output, where
   on the parent revision it printed 464 `Diff in` blocks over 14 files.
   Closed by: the command's exit status on both revisions, in the pull
   request.
2. Given this change's tree, when `mise run crate` runs, then it exits 0 and
   reports 18 passed and 0 failed. Closed by: the command's output in the
   pull request.
3. Given the parent revision, when `cargo fmt` runs on it, then the tree it
   leaves is identical to this change's tree, so the change holds nothing
   `cargo fmt` didn't write. Closed by: `git diff --exit-code` against this
   change's head exiting 0 after that run, in the pull request.
4. Given this change's tree, when `mise run all` runs, then it exits 0.
   Closed by: the gate's output and the pull request's CI run.

## What to do

Run `cargo fmt --manifest-path crates/meow/Cargo.toml` and commit its output
alone. Add no `rustfmt.toml`, so the formatter keeps its defaults for the
manifest's 2024 edition. RES-0278 found that the formatter sorts `mod` and
`use` declarations and moves 58 match arm bodies into blocks as well as
changing layout, so the tests passing after it and the formatter's own check
passing are what the pull request shows.

The reformat conflicts with every open branch that touches `crates/meow`. Say
so in the pull request, so each such branch rebases once and runs `cargo fmt`.

No unit's shipped behaviour changes, so no unit's version moves.

## Depends on

Nothing. It touches only `crates/meow/src`, so it runs in parallel with
TSK-2480.

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

The clippy findings, which TSK-2500 fixes in a change of their own, because a
hand edit beside a 464-place reformat can't be read. `mise.toml` and the
profile, which bind nothing to the formatter until TSK-2510.
