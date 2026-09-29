---
id: TSK-2930
artifact: task
status: approved
revised: 2026-09-29
bug: BUG-1301
closes: []
issue: 685
---

# Check every grouping field on every kind, and the shape of every tracker call

A fixture fails when the layout stops forbidding any field ADR-1800 forbids on
any kind, and when `meow-github project` sends anything beyond an issue's
title and body. So REQ-3320 has checks that can fail on each field and on the
tracker. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the fixture record, when a task, an epic or a defect carries any of
   `milestone`, `parent`, `project`, `sprint`, `iteration`, `label` or
   `labels`, or an epic carries `epic`, then `paw check` exits 1 naming the
   file, the line and the field. Closed by:
   `Grouping.test_every_grouping_field_is_reported_on_every_kind` in
   `plugins/meow-flow/tests/test_record.py`, seen failing against BUG-1301's
   layout.
2. Given an approved epic with two tasks, when `meow-github project` runs,
   then each call it makes reads an issue, or creates or updates one with
   exactly a title and a body. Closed by:
   `Project.test_project_groups_an_issue_nowhere` in
   `plugins/meow-github/tests/test_github.py`, seen failing against a build
   that adds `--input` to the call that creates an issue.

## What to do

Add the fixture for every field and kind, and assert the exact shape of each
call in the tracker fixture. The layout and `project` already meet REQ-3320,
so no shipped file changes and no unit's version moves. The failing run is the
suite against BUG-1301's changes, kept as evidence and then reverted, because
the checks pass against `main`.

## Depends on

Nothing.

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet.

## Left alone

`plugins/meow-flow/lib/layout.toml` and `crates/meow/src/github/project.rs`,
which meet REQ-3320. The five named `Grouping` fixtures stay, because each
states a criterion of TSK-2910.
