---
id: TSK-2340
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1510
closes: [REQ-2956, REQ-2964, REQ-3072]
issue: 547
projected: 226b4640edc2
---

# `meow-verbs evidence --keep` keeps a cited record in the repository, and `meow-verbs tree` compares it with a commit

What ADR-1530 decides for this part, in the native tool's `verbs` feature, with its fixtures. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given a current record, when `evidence --keep` runs, then the repository holds `.meowpaw/evidence/<record>.log` with the header ADR-1530 names and the whole output, and the tree id is unchanged; given a stale one, it refuses. Closed by: fixtures naming REQ-2956 and REQ-2964, seen failing first.
2. Given `evidence_dir` in the profile, when `--keep` runs, then it writes there, and the tree id leaves that directory out; bare `--keep` keeps every current verb. Closed by: fixtures naming REQ-2956.
3. Given a commit holding kept evidence, when `meow-verbs tree <commit>` runs, then it prints the kept record's tree id. Closed by: a fixture naming REQ-2956.
4. Given the `verify` skill and the implement step, when they are read, then they keep and cite the kept path and check it for secret material before committing. Closed by: the trace, naming REQ-3072.

## What to do

Change the native tool's `verbs` feature and its fixtures, state the change on `meow-verbs`' page, and move the unit to its next minor version where it hasn't moved since the last release.

## Depends on

Nothing. ADR-1530 is approved.

## Evidence

Closes REQ-2956, REQ-2964 and REQ-3072. `meow-verbs evidence format lint
test` exits 0 on this change's own tree, as the pull request cites.

The `meow-verbs` fixtures run 35 tests, OK; the five in `Kept` ran against the
program before the change and four failed. Each criterion's check:

1. `Kept.test_a_current_record_is_kept_with_its_header_and_output`,
   `Kept.test_keeping_a_record_leaves_it_current` and
   `Kept.test_a_stale_record_is_not_kept` (REQ-2956, REQ-2964).
2. `Kept.test_the_declared_directory_is_used_and_left_out`, which also keeps
   with no verb named (REQ-2956).
3. `Kept.test_a_commit_tree_matches_the_kept_record` (REQ-2956).
4. The `verify` skill's step 6 keeps, reads for secret material and cites the
   kept path, and V7 removes a file holding a secret; the implement step's
   step 4 keeps and cites the kept path (REQ-3072). `meow-author check`
   reports 0 authoring failures.

This repository declares `evidence_dir = "project/evidence"`, at the owner's
request, so its evidence sits beside the record it closes.

Two things this task found, which ADR-1550 takes up: the owner asked for
`project/evidence` as the default, and a kept `.log` file is ignored by the
common `*.log` rule in a user's global git ignore, as it is on this machine,
so it would silently stay out of the commit. The fixtures now read no global
git ignore, so they give one verdict on every machine. `meow-verbs` moves to
0.6.0 and `meow-flow` to 0.33.2.

## Left alone

The other tasks of EPC-1510.
