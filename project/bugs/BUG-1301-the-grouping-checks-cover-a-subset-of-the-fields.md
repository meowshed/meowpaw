---
id: BUG-1301
artifact: bug
status: approved
severity: minor
violates: REQ-3320
enters: cover
found: 2026-09-29
revised: 2026-09-29
issue: 685
---

# The grouping checks cover a subset of the fields ADR-1800 forbids

The `Grouping` fixtures exercise five of the twenty-two field and kind pairs
ADR-1800 forbids, so a layout that stops forbidding `project:` on every record
passes the suite, and the tracker fixture misses a grouping sent any way other
than a named flag or a field.

## Reproduction

`main` after #680, with `meow-flow` 0.39.1 built by `crates/meow/build-units`.

1. In `plugins/meow-flow/lib/layout.toml`, remove `project`, `sprint`,
   `iteration` and `labels` from the `forbidden_fields` of the epic, task and
   defect kinds, and `parent` from the task and the defect.
2. Run `python3 -m unittest test_record` in `plugins/meow-flow/tests`.
3. In `crates/meow/src/github/project.rs`, add `"--input", "grouping.json"` to
   the call that creates an issue, rebuild, and run
   `python3 -m unittest test_github` in `plugins/meow-github/tests`.

## What the system does

Every fixture passes after step 2, as it does against the shipped layout,
because the `Grouping` fixtures cover only task `milestone` and `label`, epic
`parent` and `epic`, and defect `milestone`. Every fixture passes after step 3
too, because `Project.test_project_groups_an_issue_nowhere` rejects four named
flags and any `-f` or `--field` key other than `title` or `body`, and a JSON
body sent through `--input` carries neither.

The shipped `layout.toml` holds the full lists today, so nothing is broken
yet: a later change can drop a field and pass the suite.

## What it should do, and why

A layout that drops any field ADR-1800 forbids from any kind it forbids it on
should fail a fixture, because REQ-3320 asks that a task sits under its epic
or its defect and nothing else, and EPC-1710's verification cites the
`Grouping` fixtures as the check that it does. A `project` call carrying
anything beyond the title and the body should fail the tracker fixture, for
the same requirement on the tracker.

## Triage

It enters at cover, because the layout and `project` meet REQ-3320 and the
task's checks miss most of what the requirement asks. Minor, because nothing
is broken today, and the gap lets a later change break REQ-3320 unnoticed.

## Closed by

`Grouping.test_every_grouping_field_is_reported_on_every_kind` in
`plugins/meow-flow/tests/test_record.py`, and the exact call shapes asserted
in `Project.test_project_groups_an_issue_nowhere` in
`plugins/meow-github/tests/test_github.py`, each failing against the
reproduction's changes.

## Tasks

- [x] T-001 TSK-2930 check every grouping field on every kind and the shape
      of every tracker call, in `plugins/meow-flow/tests/test_record.py` and
      `plugins/meow-github/tests/test_github.py`
      evidence: 15 checks seen failing against the reproduction's changes,
      214 `meow-flow` record fixtures and 14 `meow-github` fixtures passing,
      in #691.
