---
id: TSK-5290
artifact: task
status: approved
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

Not yet.

## Left alone

The trunk declaration `[git] trunk`, which other checks read, and the text that
describes the guard, which TSK-5291 changes.
