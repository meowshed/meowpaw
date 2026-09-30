---
id: TSK-2530
artifact: task
status: approved
revised: 2026-09-28
epic: EPC-1580
closes: [REQ-3207, REQ-3216]
issue: 616
projected: b523c09c7c9f
---

# Give `paw ready` a cover gate, and gate the implementation on the task's Cover

`paw ready` knows ten steps, `paw ready cover` takes today's implement gate,
and `paw ready implement` refuses a task until its `## Cover` names its
checks, its kept failing run, where they landed and each criterion resting on
judgement. So the program holds REQ-3207 and REQ-3216 before any
implementation starts. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given any record, when `paw ready bogus TSK-0001` runs, then it exits 2
   and its message names the ten steps in order: research, requirements,
   design, spec, epic, cover, implement, document, verify and review. Closed
   by:
   `Chain.test_an_unknown_step_names_the_ten` in
   `plugins/meow-flow/tests/test_record.py`, which replaces
   `test_an_unknown_step_names_the_nine`.
2. Given the fixture record with an approved task under an approved epic,
   when `paw ready cover TSK-0001` runs, then it exits 0; with the task set to
   draft it exits 1 naming the task as not approved; with a dependency not
   done it exits 1 naming the dependency. Closed by:
   `Cover.test_cover_is_ready_on_an_approved_task`,
   `Cover.test_cover_refuses_a_draft_task` and
   `Cover.test_cover_refuses_until_its_dependency_is_done`.
3. Given an approved, dependency-free task with no `## Cover`, when
   `paw ready implement` runs on it, then it exits 1 naming the missing Cover. Closed by:
   `Cover.test_implement_refuses_a_task_with_no_cover`.
4. Given a Cover whose `Failing run` names a path that doesn't exist, then
   `paw ready implement` exits 1 naming that path; and given one whose
   `Checks` names a path that doesn't exist, it exits 1 naming that path.
   Closed by: `Cover.test_implement_names_a_missing_failing_run` and
   `Cover.test_implement_names_a_missing_check`.
5. Given a Cover whose `Checks` names a path and whose `Landed in` is `none`,
   then `paw ready implement` exits 1 naming the `Landed in` line. Closed by:
   `Cover.test_implement_names_landed_in_left_none`.
6. Given a Cover whose `Judgement` names a criterion number with no reason,
   then `paw ready implement` exits 1 naming that criterion. Closed by:
   `Cover.test_implement_names_a_judgement_with_no_reason`.
7. Given a Cover with every line filled and every path present, then
   `paw ready implement` exits 0; and given a task whose `Checks`, `Failing run` and
   `Landed in` read `none` and whose `Judgement` names every numbered
   acceptance criterion with a reason, it exits 0. Closed by:
   `Cover.test_implement_is_ready_once_the_cover_is_filled` and
   `Cover.test_implement_is_ready_when_every_criterion_is_judgement`.
8. Given a task marked `[x]` in its epic with no `## Cover`, when `paw check`
   runs, then it reports nothing about the task. Closed by:
   `Cover.test_a_finished_task_needs_no_cover`.
9. Given an approved task at a base revision, when only its `## Cover`
   section changes and `paw check frozen --base <rev>` runs, then it reports
   0 findings; a change to its `## Acceptance criteria` in the same fixture is
   still reported. Closed by:
   `Frozen.test_a_filled_cover_leaves_an_approved_task_unchanged`.
10. Given a defect with `enters: cover` that names a requirement under
    `violates`, when `paw check` runs, then it reports nothing on `enters`;
    with `violates` empty it reports that the defect names no requirement it
    violates. Closed by: `Triage.test_a_defect_may_enter_at_cover` and
    `Triage.test_a_defect_entering_at_cover_names_what_it_violates`.
11. Given this change's tree, when `meow-verbs run format lint test` runs,
    then each passes. Closed by: the kept evidence of that run.

## What to do

In `crates/meow/src/record.rs`, `STEPS` becomes ten, with `cover` between
`epic` and `implement`, and the usage line and the unknown-step refusal print
it as they do now. `ready cover` takes what `ready implement` checks today:
the task approved, its epic or defect approved, each task under `## Depends
on` done. `ready implement` checks all that and the task's `## Cover`, as
SPC-1090's section "The gate" states: the four lines, what makes the section
filled, and one line of output for each thing missing. The Cover reading is a
function of its own, because TSK-2540's `status` calls it too.

A path under `Checks` or `Failing run` resolves against the repository root,
the directory holding `.meowpaw/profile.toml`. `Judgement` entries are
separated by semicolons, each `<number>: <reason>`. `ready` reads no history:
it doesn't check that the run failed or that the checks landed first.

`check frozen` treats `## Cover` in a task as it treats `## Evidence`, and
SPC-1070's table already says so. The `enters-fits` rule accepts `cover`
through `STEPS`, and asks a defect entering at `cover` for `violates` as it
asks one entering at `implement` or `design`.

The fixture task in `test_record.py` has no Cover, so the tests that call
`ready implement` on it, `test_implement_refuses_until_its_dependency_is_done`
among them, move to `ready cover` or give the fixture a filled Cover. The
status test that expects `next: implement` belongs to TSK-2540 and changes
there; leave `status` alone here.

Raise `meow-flow`'s minor version in `plugin.json` and its README's
`describes`, because the unit gains a gate. Write the checks first, in a
commit of their own, and see them fail.

## Depends on

Nothing. ADR-1620 and EPC-1580 are approved.

## Evidence

`crates/meow/src/record.rs` knows ten steps. `ready cover` checks what
`ready implement` checked before: the task and its epic or defect approved,
and each task under `## Depends on` done. `ready implement` checks the same
and then calls `cover_gaps`, which reads the four Cover lines and returns one
line for each thing missing. That function is separate so TSK-2540's `status`
can call it. `ready implement` skips the Cover for a task its authorising
record marks `[x]` or `[~]`. `frozen_part` treats `## Cover` as it treats
`## Evidence`, and `enters-fits` asks a defect entering at `cover` for
`violates`. `meow-flow` moves to 0.34.0, and its README describes the cover
gate and the Cover's four lines.

The 16 checks failed at the cover commit,
`0c9cec6b5c1bff9c5ea4c13d584b272c9cccb0b3`, which held the checks alone:
`meow-verbs run test` exited 1 with `FAILED (failures=16)` in the
`meow-flow` fixtures, kept as the run in #620, no longer kept. They pass
after this change:

```text
$ python3 -m unittest test_record.Cover \
    test_record.Chain.test_an_unknown_step_names_the_ten \
    test_record.Frozen.test_a_filled_cover_leaves_an_approved_task_unchanged \
    test_record.Triage.test_a_defect_may_enter_at_cover \
    test_record.Triage.test_a_defect_entering_at_cover_names_what_it_violates
Ran 16 tests
OK                                               # exit 0
$ python3 -m unittest test_record                # in plugins/meow-flow/tests
Ran 170 tests
OK                                               # exit 0
```

`git diff 0c9cec6b5c1bff9c5ea4c13d584b272c9cccb0b3 --
plugins/meow-flow/tests/test_record.py` prints no change to the 16 checks.
It shows only the two older fixtures "What to do" names, moved from
`ready implement` to `ready cover`, because the fixture task has no Cover:
`Chain.test_implement_refuses_until_its_dependency_is_done`, now
`Chain.test_cover_refuses_until_its_dependency_is_done`, and
`DefectTasks.test_a_task_under_an_approved_defect_is_ready`.

Criterion 11 is closed by the run of `meow-verbs run format lint test` kept
in this change's `project/evidence/`.

### Checks written before the change

Each criterion from 1 to 10 has a check in
`plugins/meow-flow/tests/test_record.py`, and each check failed on `main`
after #619. `meow-verbs run test` exited 1 with `FAILED (failures=16)` in the
`meow-flow` fixtures, kept as the run in #620, no longer kept:

- Criterion 1: `Chain.test_an_unknown_step_names_the_ten`, which replaces
  `test_an_unknown_step_names_the_nine`.
- Criterion 2: `Cover.test_cover_is_ready_on_an_approved_task`,
  `Cover.test_cover_refuses_a_draft_task` and
  `Cover.test_cover_refuses_until_its_dependency_is_done`.
- Criterion 3: `Cover.test_implement_refuses_a_task_with_no_cover`, and
  `Cover.test_implement_refuses_a_cover_left_not_yet`, because the epic step
  writes the section as `Not yet.` and that isn't filled either.
- Criterion 4: `Cover.test_implement_names_a_missing_failing_run` and
  `Cover.test_implement_names_a_missing_check`.
- Criterion 5: `Cover.test_implement_names_landed_in_left_none`.
- Criterion 6: `Cover.test_implement_names_a_judgement_with_no_reason`.
- Criterion 7: `Cover.test_implement_is_ready_once_the_cover_is_filled` and
  `Cover.test_implement_is_ready_when_every_criterion_is_judgement`. Each
  first asserts a refusal, with the files not landed or one criterion left
  unnamed, because `ready implement` exits 0 today and a check asserting only
  the 0 couldn't fail before the change.
- Criterion 8: `Cover.test_a_finished_task_needs_no_cover`. It asserts that
  `ready implement` refuses the task while it is open, before marking it
  `[x]`, for the same reason: `paw check` already says nothing about a
  finished task.
- Criterion 9: `Frozen.test_a_filled_cover_leaves_an_approved_task_unchanged`.
- Criterion 10: `Triage.test_a_defect_may_enter_at_cover` and
  `Triage.test_a_defect_entering_at_cover_names_what_it_violates`.

Criterion 11 has no check of its own, because it names the gate's run on the
implementing change, and that run fails today on the checks above. Its kept
evidence at the merging revision closes it. No criterion rests on judgement,
so the Cover's `Judgement` line reads `none`.

SPC-1090 gives no wording for a refusal, so the fixtures assert the exit
status and the name each refusal carries: `Cover`, the missing path,
`Landed in`, or the criterion's number.

`Chain.test_implement_refuses_until_its_dependency_is_done` and
`DefectTasks.test_a_task_under_an_approved_defect_is_ready` expect
`ready implement` to exit 0 on a task with no Cover, so they fail once the
gate lands. The implementation moves them to `ready cover` or gives the
fixture a filled Cover, as "What to do" says.

## Left alone

`paw status` and the run skill, which TSK-2540 changes. Every prompt and
template, which TSK-2550 changes, so until it lands the method skill names
nine steps while the program knows ten, and a task's Cover is written by hand
in the four lines SPC-1090 gives. The content rules of the cover step, which
ADR-1620 leaves to a later decision.
