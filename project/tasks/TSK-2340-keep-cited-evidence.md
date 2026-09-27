---
id: TSK-2340
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1510
closes: [REQ-2956, REQ-2964, REQ-3072]
issue:
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

Not yet.

## Left alone

The other tasks of EPC-1510.
