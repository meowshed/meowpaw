---
id: TSK-2910
artifact: task
status: done
revised: 2026-09-29
epic: EPC-1710
closes: [REQ-3320]
issue: 642
projected: 79a031af6d67
---

# Report a grouping field on a task, an epic or a defect, and show that `project` groups an issue nowhere

The layout forbids the grouping fields on the task, epic and defect kinds, so
`paw check` reports a record carrying one whatever its status, and a
`meow-github` test shows `project` passing no grouping argument. So a task
sits under its epic or its defect and nothing else, in the record and on the
tracker, as REQ-3320 asks. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given a task carrying `milestone:` and an epic carrying `parent:`, when
   `paw check` runs, then it reports each by file and field; given a task
   naming `epic:` or `bug:` and no grouping field, it reports nothing on the
   task. Closed by: `Grouping.test_a_task_with_a_milestone_is_reported`,
   `Grouping.test_an_epic_with_a_parent_is_reported` and
   `Grouping.test_a_task_under_its_epic_or_defect_passes` in
   `plugins/meow-flow/tests/test_record.py`.
2. Given an approved task carrying `label:`, when `paw check` runs, then it
   is reported, because a forbidden field reaches every record. Closed by:
   `Grouping.test_an_approved_task_with_a_label_is_reported`.
3. Given a defect carrying `milestone:`, and an epic carrying `epic:`, when
   `paw check` runs, then it reports each. Closed by:
   `Grouping.test_a_defect_with_a_milestone_is_reported` and
   `Grouping.test_an_epic_under_an_epic_is_reported`.
4. Given an approved epic whose task's dependency line says
   `(not blocking)`, when `meow-github project` runs against a stand-in `gh`
   that records its arguments, then no call carries `--milestone`,
   `--parent`, `--project` or `--label`, and the issue's body carries
   `(not blocking)`. Closed by:
   `Project.test_project_groups_an_issue_nowhere` in
   `plugins/meow-github/tests/test_github.py`.
5. Given this change's tree, when `meow-verbs run format lint check test build`
   runs, then each passes, and `paw check` reports no grouping field on this
   repository's record. Closed by: the kept evidence of that run.

## What to do

In `plugins/meow-flow/lib/layout.toml`, add `milestone`, `parent`, `project`,
`sprint`, `iteration`, `label` and `labels` to the `forbidden_fields` of the
task, epic and defect kinds, keeping `priority` on the defect, and add `epic`
to the epic kind's. SPC-1070's section "The layout" states the list. The
program already reports a forbidden field, so the change may be the layout
alone; if a fixture shows otherwise, change `crates/meow/src/record.rs` too.

The stand-in `gh` in `plugins/meow-github/tests/test_github.py` records its
arguments. `project` already copies the task's `## Depends on` section into
the issue's body, so the body carries the marker without a change to
`crates/meow/src/github/project.rs`; change it only if the test shows
otherwise. The test holds whether or not the other task of EPC-1710 has
landed, because the body copies the line's text as written.

Raise `meow-flow`'s minor version in `plugin.json` and its README's
`describes`, because the unit reports a new finding. If the other task of
EPC-1710 landed first, take the next minor above it. `meow-github`'s shipped
behaviour doesn't change, so its version stays unless `project.rs` changes.
Write the checks first, in a commit of their own, and see them fail.

## Depends on

Nothing. ADR-1800 and EPC-1710 are approved.

## Evidence

Done. Closes REQ-3320.

The checks failed first: the cover commit 063957639db4, rebased as 513dd310
onto main, was run
under #670, whose output is no longer kept: the `meow-flow` suite exited 1 with
seven failures, one for each `Grouping` test and two for the subtests of
`test_a_task_under_its_epic_or_defect_passes`.

The change is the layout alone: `crates/meow/src/record.rs` already reports a
forbidden field, and `crates/meow/src/github/project.rs` is unchanged.

`python3 -m unittest test_record.Grouping`, from
`plugins/meow-flow/tests`, exited 0 and printed `Ran 6 tests` and `OK`. The
whole file, `python3 -m unittest test_record`, exited 0 and printed
`Ran 209 tests` and `OK`. `python3 -m unittest test_github`, from
`plugins/meow-github/tests`, exited 0 and printed `Ran 14 tests` and `OK`,
`Project.test_project_groups_an_issue_nowhere` among them.

`plugins/meow-flow/bin/paw check` exited 0 and printed 0 findings for every
check, with the coverage line `792 of 1107 requirements in force land in a
task`, so no record in this repository carries a grouping field.

`git diff 063957639db42685ae09fc0c895789e45fa19973 --
plugins/meow-flow/tests/test_record.py plugins/meow-github/tests/test_github.py`
printed nothing, so the checks are as the cover wrote them.

The five verbs' run is kept under `project/evidence/` in this change.

## Left alone

The dependency marker, `dependency-declared` and readiness, which the other
task of EPC-1710 carries. Projecting the epic onto a tracker grouping
(REQ-1364) and a blocking dependency onto GitHub's blocked-by relation, which
ADR-1800 leaves to a tracker decision. A grouping under a field name outside
the list, such as `group:`, which ADR-1800 leaves unreported. SPC-1070 and
SPC-1080, already updated with the epic.
