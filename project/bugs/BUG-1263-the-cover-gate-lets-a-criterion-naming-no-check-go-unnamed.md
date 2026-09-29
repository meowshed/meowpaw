---
id: BUG-1263
artifact: bug
status: approved
severity: major
violates: REQ-3216
enters: design
found: 2026-09-29
revised: 2026-09-29
issue: 676
---

# `paw ready implement` lets a criterion that names no check go unnamed once any check is listed

`paw ready implement` exits 0 on a Cover whose `Checks` names a file and whose
`Judgement` leaves out a criterion that names no evidence to close it. So that
criterion reads as covered while nothing covers it, which REQ-3216 exists to
prevent. The gate also takes a reason with no word in it, such as `.` or `-`.

## Reproduction

`main` after #666, with `meow-flow` built by `crates/meow/build-units`.

1. Take the fixture record in `plugins/meow-flow/tests/test_record.py`: an
   approved epic and an approved open task, TSK-0001, with
   `tests/test_a_task.py` and `project/evidence/a-failing-run.txt` present.
2. Give the task the criteria `1. Given a task, then a check passes. Closed
by: tests/test_a_task.py.`, `2. Given a page, then it reads well.` and
   `3. Given a table, then it is ordered as a reader expects.`, and the Cover
   `Checks: tests/test_a_task.py`, `Failing run:
project/evidence/a-failing-run.txt`, `Landed in: #12`, `Judgement: none`.
3. Run `paw ready implement TSK-0001`.
4. Set `Judgement` to `2: .; 3: -`, and run it again.

## What the system does

Both runs exit 0 and print
`paw ready implement: ready; TSK-0001 approved and complete`. `cover_gaps` in
`crates/meow/src/record.rs` asks `Judgement` to name every criterion only
where `Checks` reads `none`, the rule BUG-1261 added, and takes any text after
the colon as a reason.

## What it should do, and why

`ready implement` should exit 1, naming each criterion that carries no
`Closed by:` and isn't named under `Judgement`, and each `Judgement` entry
whose reason holds no letter. The task template asks every criterion to name
the evidence that will close it on a `Closed by:` line, so a criterion without
one names nothing that checks it, and it rests on judgement unless the task
says otherwise. REQ-3216 asks that such a criterion is named with its reason
before the implementation starts, and `.` gives no reason.

BUG-1261 left this case to the cover step's instructions, because the program
can't tell which criteria no program can check. The `Closed by:` line gives it
a reading it can make: the task itself says which criteria name a check. The
gate still doesn't judge whether the evidence a `Closed by:` line names can
settle its criterion, or whether a reason with letters in it is a good one.

## Triage

It enters at design, because REQ-3216 is right and the rule BUG-1261 states in
SPC-1090 is too weak to hold it once a check is listed. That rule is approved
and frozen with BUG-1261, so this record states the corrected rule, and
SPC-1090's section "The gate" carries it. Major, because the gate that holds
REQ-3216 passes the Cover the requirement forbids.

## Closed by

The reproduction as fixtures in the class `CoverClosedBy` in
`plugins/meow-flow/tests/test_record.py`: a criterion with no `Closed by:` left
out of `Judgement`, and reasons with no letter, each refused naming the
criterion, and a criterion with no `Closed by:` named under `Judgement`,
accepted.

## Tasks

- [x] T-001 TSK-2573 refuse a criterion that names no check and isn't under
      Judgement, in `crates/meow/src/record.rs`
      evidence: 2 checks seen failing first, 215 `meow-flow` fixtures
      passing, in #678.
