---
id: TSK-5290
artifact: task
status: done
revised: 2026-10-10
epic: EPC-2770
closes: [REQ-4412]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The readiness check reads a task's approval from the working tree

`paw ready implement` and `paw status` read a task's approval from the working tree and
not from the trunk, so a task approved on the epic's own branch is ready.

## Acceptance criteria

1. Given a task approved in the working tree and absent from the trunk, when
   `paw ready implement` runs for it, then it exits 0. Closed by: a test in
   `plugins/meow-flow/tests/test_record.py`.
2. Given the same task, when `paw status` runs, then it prints `next: implement`
   for it and no `waiting:` line. Closed by: a test in the same file.
3. Given a task that is a draft in the working tree, when `paw ready implement`
   runs for it, then it exits 1 and names the task. Closed by: a test in the
   same file.

## What to do

Remove the read of the trunk from the readiness check and from the status
line, with the tests that held the withdrawn guard (REQ-3660, REQ-3662,
REQ-3664), in a commit of their own that says why. Keep the check that a task's
blocking dependency is done in the working tree.

## Depends on

Nothing.

## Evidence

Pull request 880. The tests are in `plugins/meow-flow/tests/test_record.py`,
class `ApprovedOnTheBranch`:

- Criterion 1: `test_a_task_approved_on_the_branch_is_ready`.
- Criterion 2: `test_status_names_the_task_as_next`.
- Criterion 3: `test_a_draft_task_is_not_ready`.

The tests of the withdrawn guard, 22 in the class `OffTheTrunk`, were removed in a
commit of its own that says why. This task changed the guard that would have
refused it, so `paw ready implement TSK-5290` couldn't be run before the change
on this branch, and the owner's instruction to work this epic by the new rules
is what authorised starting it. `meow-checks run format lint check test build`
ran on the final tree; its result is in the pull request's `gate` job.

## Left alone

The trunk declaration `[git] trunk`, which other checks read, and the text that
describes the guard, which TSK-5291 changes.
