---
id: TSK-2500
artifact: task
status: approved
revised: 2026-09-28
epic: EPC-1570
closes: []
issue:
---

# Fix the crate's clippy findings

The crate passes clippy's default set with warnings denied, fixed by
`cargo clippy --fix` where it can and by hand for the rest, as ADR-1610's
third change decides. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given this change's tree, when `cargo clippy --quiet --manifest-path
crates/meow/Cargo.toml --all-features --all-targets -- -D warnings` runs,
   then it exits 0 with no output, where on the parent revision it exited 101
   on 15 errors. Closed by: the command's exit status on both revisions, in
   the pull request.
2. Given this change's tree and its parent, when `mise run crate` runs on
   each, then both exit 0 and report 18 passed and 0 failed. Closed by: both
   outputs in the pull request.
3. Given this change's tree, when `cargo fmt --manifest-path
crates/meow/Cargo.toml --check` runs, then it exits 0, so the fixes keep
   TSK-2490's form. Closed by: the command's exit status in the pull request.
4. Given the branch's commits, when a reviewer reads them, then the first
   holds only what `cargo clippy --fix` wrote and the second holds the hand
   edits for `skip_while_next` and `regex_creation_in_loops`. Closed by:
   judgement, because only a reader can tell that the second commit's edits
   keep each function's behaviour; the first can be checked by running
   `cargo clippy --fix` on the parent and comparing.
5. Given this change's tree, when `mise run all` runs, then it exits 0.
   Closed by: the gate's output and the pull request's CI run.

## What to do

Run `cargo clippy --fix --allow-dirty --manifest-path crates/meow/Cargo.toml
--all-features --all-targets`, then `cargo fmt`, and commit that alone.
RES-0278 found that it fixes 13 of the 15 findings, in `record.rs`,
`author.rs` and `git.rs`. Edit the two it leaves by hand in a second commit:
`skip_while_next` and `regex_creation_in_loops`. Allow no lint with an
attribute, because an allowed finding passes the lint and still ships.

The pull request squashes to one commit, so name both parts in its body. The
review reads the two branch commits apart.

No unit's shipped behaviour changes, so no unit's version moves.

## Depends on

TSK-2490, because the reformat rewrites the lines these fixes touch, and
fixes written first would conflict with it.

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

Clippy's lints outside its default set, which ADR-1610 leaves open. Each
feature alone, which the crate passes today (RES-0278) and ADR-1610 leaves
unchecked. `mise.toml` and the profile, which bind nothing to clippy until
TSK-2510.
