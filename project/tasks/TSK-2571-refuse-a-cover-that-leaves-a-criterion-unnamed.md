---
id: TSK-2571
artifact: task
status: approved
revised: 2026-09-28
bug: BUG-1261
closes: []
issue: 650
---

# Refuse a Cover that leaves a criterion nothing checks unnamed

`paw ready implement` refuses a Cover with `Checks: none` that leaves any
criterion out of `Judgement`, a task with no numbered criterion, a
`Judgement` number that matches no criterion, and a Cover line left empty. So
no criterion that nothing checks reads as covered when the implementation
starts. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given an approved open task with criteria 1 and 2, when its Cover reads
   `Checks: none`, names a failing run and a pull request, and
   `Judgement: none`, then `paw ready implement` exits 1 with a line for each
   of criteria 1 and 2. Closed by: the class `CoverCriteria` in
   `plugins/meow-flow/tests/test_record.py`.
2. Given an approved open task whose `## Acceptance criteria` holds bullets
   and no numbered criterion, or has no such section, when
   `paw ready implement` runs, then it exits 1 saying the task names no
   numbered criterion. Closed by: the class `CoverCriteria`.
3. Given a Cover whose `Judgement` names criterion 7 on a task with criteria 1
   and 2, when `paw ready implement` runs, then it exits 1 with a line naming 7. Closed by: the class `CoverCriteria`.
4. Given a Cover whose `Judgement:` line is empty, when
   `paw ready implement` runs, then it exits 1 with a line naming
   `Judgement`. Closed by: the class `CoverCriteria`.
5. Given a Cover whose `Checks` names a check, whose run and pull request are
   named, and whose `Judgement` names a criterion that exists, with its
   reason, when `paw ready implement` runs, then it exits 0. Closed by:
   `Cover.test_implement_is_ready_once_the_cover_is_filled`, on a task that
   now carries numbered criteria.

## What to do

In `cover_gaps` in `crates/meow/src/record.rs`, apply BUG-1261's rule: a
task with no numbered criterion is refused, an empty Cover line is refused,
a `Judgement` number matching no criterion is refused, and `Checks: none`
asks `Judgement` to name every criterion whatever the other two lines say.
Give the `Cover` fixtures' task numbered criteria, because the gate now reads
them on every Cover. State the rule in SPC-1090's section "The gate".

`meow-flow` 0.35.0 isn't released yet, so the fix ships in it without a
version of its own. Write the checks first, in a commit of their own, and see
them fail.

## Depends on

Nothing. BUG-1261 is approved, and TSK-2570 has landed.

## Evidence

`cover_gaps` in `crates/meow/src/record.rs` now refuses an empty Cover line, a
task with no numbered criterion, and a `Judgement` number that matches no
criterion. With `Checks: none` it asks `Judgement` to name every criterion
whatever `Failing run` and `Landed in` say, and returns early only where both
read `none` as well. The `Cover` fixtures' task carries three numbered
criteria, because the gate reads them on every Cover. SPC-1090's section "The
gate" states the rule.

The five checks in the class `CoverCriteria` failed first: `meow-verbs run
test` exited 1 with `FAILED (failures=5)`, kept as
`project/evidence/f6f0644bf46f.txt`, in the commit that held the checks alone.
They pass now:

```text
$ python3 -m unittest test_record    # in plugins/meow-flow/tests
Ran 190 tests
OK                                   # exit 0
```

`meow-flow` 0.35.0 isn't released yet, so this fix ships in it without a
version of its own. `meow-verbs evidence --keep format lint check test build`
exits 0 on this change's own tree, each result kept in `project/evidence/`,
as the pull request cites.

## Left alone

A Cover whose `Checks` names a check and whose `Judgement` leaves out a
criterion no program can check: the program can't tell which criteria the
checks cover, so `steps/cover.md` holds that case. A per-criterion mapping
from criterion to check, which would reach it, is a decision of its own.
