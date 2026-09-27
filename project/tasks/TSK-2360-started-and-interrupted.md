---
id: TSK-2360
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1510
closes: [REQ-2968, REQ-2969]
issue: 549
projected: 3e6df76eafe3
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

Closes REQ-2968 and REQ-2969. `meow-verbs evidence format lint test` exits 0
on this change's own tree, each result kept in `project/evidence/`, as the
pull request cites.

The three `Interrupted` fixtures failed on the program before the change, and
the `meow-verbs` suite now runs 51 tests, OK:

1. `test_a_started_run_whose_process_lives_is_running` and
   `test_a_started_run_whose_process_is_gone_is_interrupted`: a start with no
   end reads as `running` while its process, matched by id and start time on
   this host, lives, and as `interrupted` otherwise, each exiting 4 (REQ-2968).
2. `test_a_verb_ended_by_a_signal_is_interrupted`: a verb ended by SIGTERM is
   recorded as `interrupted`, and `run` and `evidence` exit 4 (REQ-2969).

The `verify` skill's V2 and `meow-verbs`' page state the fourth outcome and
exit status. The fixtures' ledger reader now pairs a started line with its end,
as the program does.

## Left alone

The other tasks of EPC-1510.
