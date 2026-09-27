---
id: TSK-2360
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1510
closes: [REQ-2968, REQ-2969]
issue:
---

# `meow-verbs` records a verb as started and ended, and reports `interrupted` and `running`

What ADR-1530 decides for this part, in the native tool's `verbs` feature, with its fixtures. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given a started record with no end, when `evidence` runs, then it reports `running` while that process lives and `interrupted` after, exiting 4. Closed by: fixtures naming REQ-2968, seen failing first.
2. Given a verb ended by an interrupt or termination signal, when `run` records it, then its outcome is `interrupted` and `run` exits 4 where none failed. Closed by: a fixture naming REQ-2969.

## What to do

Change the native tool's `verbs` feature and its fixtures, state the change on `meow-verbs`' page, and move the unit to its next minor version where it hasn't moved since the last release.

## Depends on

TSK-2350, whose lock every write takes.

## Evidence

Not yet.

## Left alone

The other tasks of EPC-1510.
