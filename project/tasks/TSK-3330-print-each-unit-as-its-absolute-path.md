---
id: TSK-3330
artifact: task
status: approved
revised: 2026-09-29
bug: BUG-1341
closes: []
issue: 682
---

# Print and record each unattended unit as its absolute path

`meow-unattended plan` prints each `--plugin-dir` and records each snapshot
unit `path` as the unit directory's absolute path with every symbolic link
resolved, so the printed command loads the declared units wherever it runs.
One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given a profile declaring two units, when `plan` runs in a subdirectory of
   the repository, then it exits 0, prints exactly two `--plugin-dir`
   arguments, each absolute and naming one declared unit's directory in the
   declared order, and the snapshot's two unit `path` values are the same two
   absolute paths. Closed by:
   `Units.test_unit_paths_hold_from_a_subdirectory` in
   `plugins/meow-unattended/tests/test_unattended.py`.
2. Given this change's tree, when `meow-verbs run format lint check test
build` runs, then each passes. Closed by: the kept evidence of that run.

## What to do

In `crates/meow/src/unattended.rs`, resolve each unit's directory against
the repository root and canonicalise it when `unit()` reads the manifest,
then use that path for `--plugin-dir` and for the snapshot's `units[].path`.
Keep the declared entry in the resolved `[unattended]` table and in the
output's list of units, because that table is what the repository declared.
State the absolute path in SPC-1200's sections "The command line" and "The
snapshot". Raise `meow-unattended` to 0.2.2 in `plugin.json`, and its
README's `describes:` with it.

Write the check first, in a commit of its own, and see it fail.

## Depends on

Nothing. BUG-1341 is approved, and TSK-3320 has landed.

## Evidence

`unit()` in `crates/meow/src/unattended.rs` now keeps the unit directory it
read the manifest from, resolved against the repository root and
canonicalised, and `plan` prints that path after `--plugin-dir` and stores it
as the snapshot's `units[].path`. The resolved table and the output's list of
units keep the declared entry. SPC-1200's sections "The command line" and "The
snapshot" and the unit's README state the absolute path. `meow-unattended` is
0.2.2.

The check failed first: `meow-verbs run test` exited 1 with
`FAILED (failures=1)` on `Units.test_unit_paths_hold_from_a_subdirectory`,
which read `['units/alpha', 'units/beta']` where it expected the absolute
paths, kept as the run in #683, no longer kept in the commit that held the
check alone. It passes now, unchanged:

```text
$ python3 -m unittest test_unattended    # in plugins/meow-unattended/tests
Ran 19 tests
OK                                       # exit 0
```

Criterion 2: `meow-verbs run format lint check test build` passes on this
change's tree, and `meow-verbs evidence --keep` keeps each result in
`project/evidence/`, as the pull request cites.

## Left alone

Printing a `cd` to the root before the command, which would also work but
leaves the snapshot's paths relative to a directory the snapshot doesn't
name. Checking at start that each named unit loaded, which ADR-2000 gives to
the decision that starts a run.
