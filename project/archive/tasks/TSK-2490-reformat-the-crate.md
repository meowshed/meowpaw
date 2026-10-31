---
id: TSK-2490
artifact: task
status: done
revised: 2026-09-28
epic: EPC-1570
closes: []
issue: 603
projected: df9b90d49484
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

`cargo fmt --manifest-path crates/meow/Cargo.toml` rewrote 15 files under
`crates/meow/src`, and the change holds nothing else in the crate. No
`rustfmt.toml` was added.

Both checks in `tools/test_crate_format.py` failed at the cover commit,
1605c55, which held the checks alone, and pass after this change:

```text
$ TSK_2490_BASE=dbbd309 python3 -m unittest tools/test_crate_format.py    # checks alone
AssertionError: 1 != 0 : 495 Diff in blocks
AssertionError: Lists differ: ['author.rs', 'git.rs', 'github.rs', ...] != []
Ran 2 tests
FAILED (failures=2)                                    # exit 1
$ TSK_2490_BASE=dbbd309 python3 -m unittest tools/test_crate_format.py    # this change
Ran 2 tests
OK                                                     # exit 0
$ cargo fmt --manifest-path crates/meow/Cargo.toml --check
                                                       # exit 0, no output
$ mise run crate
test result: ok. 29 passed; 0 failed; 0 ignored        # exit 0
```

A diff of `tools/test_crate_format.py` against 1605c55 prints nothing. The
kept evidence of `meow-verbs run format lint test` sits in
`project/evidence/`, committed with this change.

### Checks written before the change

Each criterion a program can check has a check in
`tools/test_crate_format.py`, and each check failed on the parent revision,
`main` after #607:

- Criterion 1: `FormatterCheck.test_cargo_fmt_check_exits_0_with_no_output`.
  On that revision it counted 495 `Diff in` blocks over 15 files, not the 464
  over 14 that criterion 1 states, because changes merged after the task was
  written added code to the crate.
- Criterion 3:
  `NothingButTheFormatter.test_formatting_the_parent_gives_this_tree`. It
  reads the parent from `TSK_2490_BASE` and is skipped without it, because
  the criterion concerns one change, and any default parent turns it false
  once a later change edits the crate. It checks `crates/meow/src` and any
  `rustfmt.toml`, and not the whole tree, since the file holding the checks
  is itself part of the change.

Criterion 2 is judgement, although a program runs it: `mise run crate`
already passes before the change, so no check can fail first and show that
the reformat did anything. The existing `crate` task is the check, and the
pull request shows its output. On that revision it reported 29 passed and 0
failed, not the 18 criterion 2 states, for the same reason as the block
count.

Criterion 4 is judgement for the same reason: the gate passes before the
change, so the gate's own run and the pull request's CI run are the check.

## Left alone

The clippy findings, which TSK-2500 fixes in a change of their own, because a
hand edit beside a 464-place reformat can't be read. `mise.toml` and the
profile, which bind nothing to the formatter until TSK-2510.
