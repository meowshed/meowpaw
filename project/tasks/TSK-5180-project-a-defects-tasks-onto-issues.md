---
id: TSK-5180
artifact: task
status: approved
revised: 2026-10-03
realises: ADR-2760
closes: [REQ-4000]
issue: 829
projected: 467c47e0c430
---

# Project a defect's tasks onto issues

Make `meow-github project BUG-NNNN` project and check the active tasks an
approved defect carries through the same durable mapping as epic tasks. One
task, one branch, one pull request and one review.

## Acceptance criteria

1. Given an approved defect carrying a task, when `project BUG-NNNN` runs,
   then it creates or updates the task's issue, records the mapping and names
   the defect in the issue body. Closed by: a `Project` fixture.
2. Given that projection, when it replays or runs with `--check`, then replay
   writes nothing and check reports disagreement without writing. Closed by:
   `Project` fixtures inspecting tracker calls.
3. Given open and closed task marks on the defect, when `--check` reads the
   issue state, then it compares completion with the defect's mark. Closed by:
   a `Project` fixture.
4. Given the shipped command and documentation, when a reader looks for valid
   targets, then both name `BUG-NNNN`. Closed by: launcher and documentation
   checks.

## What to do

Generalise target resolution and projection prose without creating a second
synchronisation path. Preserve request-layer budgets, mapping fingerprints,
partial outcomes, read-back and the prohibition on tracker grouping. Update
SPC-1080, the unit page and launcher fallback usage to match the interface.

## Depends on

Nothing.

## Evidence

`Project.test_an_approved_defect_projects_its_task_and_replays_nothing`
closes criteria 1 and 2. `Project.test_a_defect_mark_decides_whether_a_closed_issue_agrees`
closes criterion 3. The launcher fallback and unit page changes close criterion
4 through `mise run all`'s shell and Markdown checks. All 55 `meow-github`
fixtures passed, the repository's format, check, lint and test verbs passed in
`mise run all`, and the build verb passed in `crates/meow/build-units`. Pull
request: #830.

## Left alone

Projecting the defect record itself and tracker-native grouping remain outside
ADR-2760.
