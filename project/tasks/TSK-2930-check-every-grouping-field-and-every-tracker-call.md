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

## Evidence

`Grouping.test_every_grouping_field_is_reported_on_every_kind` in
`plugins/meow-flow/tests/test_record.py` writes each of the twenty-two field
and kind pairs ADR-1800 forbids and asserts that `paw check` reports the file,
the line and the field. `Project.test_project_groups_an_issue_nowhere` in
`plugins/meow-github/tests/test_github.py` now asserts the exact shape of each
call: a read of `repos/o/r/issues/N`, or a `POST` or `PATCH` carrying exactly
`-f title=` and `-f body=`.

The checks pass against `main`, whose layout and `project` meet REQ-3320, so
each failing run is against one of BUG-1301's changes. With BUG-1301's layout,
`meow-verbs run test` exited 1 with `FAILED (failures=14)`, one for each pair
the layout dropped, kept as `project/evidence/b7f2e915005c.txt`. With
`--input grouping.json` added to the call that creates an issue, it exited 1
with `FAILED (failures=1)` in `test_github`, `10 != 8` on that call, kept as
`project/evidence/1a1954963195.txt`. Each change was then reverted and the
units rebuilt, and both suites pass:

```text
$ python3 -m unittest plugins/meow-flow/tests/test_record.py
Ran 214 tests
OK                                   # exit 0
$ python3 -m unittest test_github    # in plugins/meow-github/tests
Ran 14 tests
OK                                   # exit 0
```

No shipped behaviour changes, so no unit's version moves.
`meow-verbs evidence --keep format lint check test build` exits 0 on this
change's own tree, each result kept in `project/evidence/`, as the pull
request cites.

## Left alone

`plugins/meow-flow/lib/layout.toml` and `crates/meow/src/github/project.rs`,
which meet REQ-3320. The five named `Grouping` fixtures stay, because each
states a criterion of TSK-2910.
