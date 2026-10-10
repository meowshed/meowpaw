---
id: TSK-5311
artifact: task
status: done
revised: 2026-10-10
epic: EPC-2800
closes: [REQ-4600]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# `paw done`

`paw done <task> --pr <number>` closes a complete task in one step.

## Acceptance criteria

1. Given a task with its Evidence written, when `paw done TSK-1 --pr 12` runs,
   then the task stores `done`, its epic's mark is `[x]` with `(done: pull
request 12)`, and `paw check` accepts the tree. Closed by: a test in
   `plugins/meow-flow/tests/test_record.py`.
2. Given the last open task of an epic and its decision, when the command runs,
   then the epic and the decision store `done`. Closed by: a test in the same
   file.
3. Given a task whose Evidence still opens with `Not yet.`, when the command
   runs, then it exits 1 and changes nothing. Closed by: a test in the same file.

## What to do

Add the subcommand, mark through the same writer TSK-5310 uses, and name the
pull request number as the person gave it.

## Depends on

- TSK-5310 (not blocking): the two share the writer that changes a status line.

## Evidence

Pull request 884. The tests are in `plugins/meow-flow/tests/test_record.py`,
class `WriteCommands`:

- Criterion 1: `test_done_closes_the_task_its_epic_and_the_decision` and
  `test_done_leaves_the_epic_open_while_another_task_is_open`.
- Criterion 2: `test_done_closes_the_task_its_epic_and_the_decision`.
- Criterion 3: `test_done_refuses_a_task_whose_evidence_is_not_written`.

This task and TSK-5310 were closed with the command: `paw done TSK-5310 --pr
884` and `paw done TSK-5311 --pr 884` stored `done`, marked the entries and
closed EPC-2800 and ADR-2880.

## Left alone

The project index's prose and the research synthesis, which a person writes.
