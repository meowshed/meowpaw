---
id: BUG-1180
artifact: bug
status: approved
severity: major
violates: REQ-0584
found: 2026-09-26
revised: 2026-09-26
issue: 406
---

# A task marked `[P]` derives as open whatever its mark

## Reproduction

With `meow-method` 0.30.0, on the trunk after #403, in this repository:

```text
$ plugins/meow-method/bin/paw show REQ-1050
State
  in a task not yet done
  TSK-1160 open in EPC-1010, verified under #118
```

EPC-1010 lists that task as `- [x] T-006 [P] TSK-1160 ...`, with its evidence.
In a scratch record, the fixture `test_a_task_marked_parallel_is_read_with_its_mark`
marks the one task `- [x] T-001 [P] TSK-0001` and gets the same result.

## What the system does

The program reads an epic's task entries with a pattern that expects the
task's identifier straight after its number, so an entry carrying `[P]`
between them is never read. Its task has no mark, which derives as open.
Eight entries in EPC-1000 and EPC-1010 carry `[P]`, and `paw status` counted
13 requirements their tasks close as in a task not yet done, 545 verified in
all where 558 are. `check rules` reads entries with the same pattern, so a
parallel task marked done with no evidence went unreported.

## What it should do, and why

An observed status is derived from the tree (REQ-0584), and the tree marks
those tasks done, so the derivation has to read them. The epic step asks for
the tasks that can run in parallel to be marked (REQ-0265), and `[P]` is the
form both epics use, although the template and SPC-1090 never stated one: the
fix states it in both.

## Triage

Implementation, in `meow record`. Major, because it misreports the record's
state in every `status` and `show`, and hides a missing evidence finding,
while `check` reports nothing wrong.

## Closed by

Both patterns read an optional `[P]` after the task's number. The fixtures
`test_a_task_marked_parallel_is_read_with_its_mark` and
`test_a_task_marked_parallel_and_done_carries_evidence` fail against 0.30.0
and pass against the fix, and `paw status` counts 558 requirements verified.
The epic template and SPC-1090 state the form.
