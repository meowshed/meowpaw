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

## Cover

Not yet.

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

`paw status` and the run skill, which TSK-2540 changes. Every prompt and
template, which TSK-2550 changes, so until it lands the method skill names
nine steps while the program knows ten, and a task's Cover is written by hand
in the four lines SPC-1090 gives. The content rules of the cover step, which
ADR-1620 leaves to a later decision.
