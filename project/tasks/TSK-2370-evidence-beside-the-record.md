---
id: TSK-2370
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1520
closes: [REQ-2956]
issue:
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

Not yet.

## Left alone

Files kept before ADR-1550, of which there are none.
