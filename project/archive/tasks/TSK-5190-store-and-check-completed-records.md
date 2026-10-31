---
id: TSK-5190
artifact: task
status: done
revised: 2026-10-04
realises: ADR-2770
closes: [REQ-0583, REQ-0585, REQ-0594, REQ-0595, REQ-0596]
issue: 832
projected: bdb0c889f343
---

# Store and check completed records

Decisions, epics and tasks state `status: done` in the same change that makes
their derived completion true, and the record gate rejects disagreement in
either direction. Existing completed records migrate in this pull request.

## Acceptance criteria

1. Given a decision, epic or task, when its stored `done` value disagrees with
   derived completion in either direction, then `paw check` names the record
   and the disagreement; matching states pass. Closed by: record fixtures for
   all three kinds and both disagreement directions.
2. Given a `done` decision, epic or task, when readiness, tracker projection or
   the frozen check reads it, then it is accepted as post-approval while a
   simultaneous substantive edit remains rejected. Closed by: focused ready,
   projection and frozen-check fixtures.
3. Given a grandfathered task with no authorising relation, when its Evidence
   is non-placeholder, then it derives complete and accepts `done`. Closed by:
   a focused record fixture covering empty and completed Evidence.
4. Given the repository at the migration baseline, when the migration runs,
   then every derived-complete decision, epic and task stores `done`, every
   open one remains `approved`, and artifact totals remain unchanged. Closed
   by: `paw count` before and after plus `paw check` over the migrated tree.
5. Given an author completing future work, when they read the constitution,
   templates and unit documentation, then each tells them to write `done` with
   the task's marks or Evidence in the same pull request. Closed by: the
   repository's Markdown and documentation checks.

The repository's definition of done applies as well and isn't restated here.

## What to do

Implement ADR-2770's single completion calculation across checking, readiness,
projection and frozen-record comparison. Expand the parser to accept the new
status before migrating structured front matter, update the living contract
and authoring surfaces, migrate only records the calculation proves complete,
then leave no compatibility path in which derived completion can remain
`approved`. Preserve every artifact count and do not add `done` to another
kind.

## Depends on

Nothing.

## Evidence

PR #833 implements and migrates the checked completion status. On 2026-10-04,
the repository's five declared verification verbs all exited 0:
`mise run fmt-check && mise run shell-fmt && mise run crate-fmt`,
`mise run crate-check`, the complete `.meowpaw/profile.toml` lint command, the
complete profile test command under Python 3.13, and `mise run build`. The test
verb included 281 meow-flow tests, 58 meow-github tests, 103 meow-loop tests,
`paw check`, and the repository integrity tools. `paw count` retained 1,954
identifiers while classifying 74 decisions, 70 epics and 225 tasks as `done`.

## Left alone

Tracker issue state and completion statuses for requirements, defects,
research and other artifact kinds, because ADR-2770 does not change them.
