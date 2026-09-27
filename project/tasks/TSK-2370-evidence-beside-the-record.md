---
id: TSK-2370
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1520
closes: [REQ-2956]
issue: 553
projected: b441f9437f19
---

# `evidence --keep` writes `<record root>/evidence/<record>.txt` and reports a kept file git ignores

The evidence directory defaults to the record's root with `evidence` under
it, kept files end in `.txt`, and `--keep` checks each file it wrote against
git's ignore rules. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given no `evidence_dir`, when `--keep` runs, then it writes
   `project/evidence/<record>.txt`, or `<root>/evidence/<record>.txt` where the
   profile declares `[record] root`; given `evidence_dir`, it writes there.
   Closed by: fixtures naming REQ-2956, seen failing first.
2. Given an ignore rule matching the kept file, when `--keep` runs, then it
   names the file and the rule, leaves the file and exits 1; given a
   directory that isn't a git work tree, it says it couldn't check and exits 3. Closed by: fixtures naming REQ-2956.
3. Given a kept file under `project/evidence`, when `paw check` runs on this
   repository, then it exits 0. Closed by: its output.

## What to do

Change the native tool's `verbs` feature and its fixtures, state the default
on `meow-verbs`' page, and remove `evidence_dir` from this repository's
profile, which now repeats the default.

## Depends on

Nothing. ADR-1550 is approved.

## Evidence

Closes REQ-2956. `meow-verbs evidence format lint test` exits 0 on this
change's own tree, and each result is kept in `project/evidence/`, the first
evidence this repository keeps, as the pull request cites.

The `meow-verbs` fixtures run 38 tests, OK; the four `Kept` fixtures this task
changed or added failed on the program before it. Each criterion's check:

1. `Kept.test_a_current_record_is_kept_with_its_header_and_output` writes
   `project/evidence/<record>.txt` with no declaration,
   `Kept.test_the_default_follows_a_moved_record` follows `[record] root`, and
   `Kept.test_the_declared_directory_is_used_and_left_out` obeys
   `evidence_dir` (REQ-2956).
2. `Kept.test_a_kept_file_git_ignores_is_reported_and_left` exits 1 naming
   `.gitignore:1`, and `Kept.test_outside_git_a_kept_file_is_unchecked` exits
   3 (REQ-2956).
3. `paw check` passes with this task's own kept files under
   `project/evidence/`, run by the `test` verb.

This repository's profile no longer declares `evidence_dir`, which repeated
the default.

## Left alone

Files kept before ADR-1550, of which there are none.
