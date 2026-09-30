---
id: TSK-2920
artifact: task
status: approved
revised: 2026-09-29
bug: BUG-1300
closes: []
issue: 679
---

# Show `paw status` waiting on a blocking dependency

A fixture fails when `paw status` stops waiting on a blocking dependency, and
each `dependency-declared` fixture shows its line reported by that rule. So
REQ-1358's `status` half has a check that can fail. One task, one branch, one
pull request, one review.

## Acceptance criteria

1. Given the `Dependencies` fixture with the epic listing TSK-0002 first, when
   TSK-0002's only dependency line is `(blocking)`, or bare on an approved
   task, then `paw status` names TSK-0001 as next and not TSK-0002. Closed by:
   `Dependencies.test_status_waits_on_a_blocking_dependency` in
   `plugins/meow-flow/tests/test_record.py`, seen failing against BUG-1300's
   build.
2. Given a draft task with a variant marker, a bare line or a line naming two
   tasks, when `paw check rules` runs, then the line is reported with
   `dependency-declared`'s own message. Closed by:
   `test_a_declared_dependency_passes`,
   `test_a_bare_dependency_in_a_draft_is_reported` and
   `test_a_line_naming_two_tasks_is_reported`.

## What to do

Add the contrast case to the `Dependencies` fixtures and assert the rule's
message in the three `dependency-declared` fixtures. The program already
meets REQ-1358, so no code changes and no unit's version moves. The failing
run is the suite against BUG-1300's build, kept as evidence and then
reverted, because the checks pass against `main`.

## Depends on

Nothing.

## Evidence

`Dependencies.test_status_waits_on_a_blocking_dependency` in
`plugins/meow-flow/tests/test_record.py` gives TSK-0002 a `(blocking)` line,
then a bare line on the approved task, with the epic listing TSK-0002 first,
and asserts that `paw status` names TSK-0001 as next. The three
`dependency-declared` fixtures now assert the rule's message on the reported
line.

The checks pass against `main`, whose code meets REQ-1358, so the failing run
is against BUG-1300's build: `.map(|_doc| true)` in place of the dependency
test in `paw status`. `meow-verbs run test` exited 1 with
`FAILED (failures=2)`, one failure for each line of the new fixture, kept as
the run in #680, no longer kept, whose tree is that build's. The change
was then reverted and the units rebuilt, and the suite passes:

```text
$ python3 -m unittest plugins/meow-flow/tests/test_record.py
Ran 213 tests
OK                                   # exit 0
```

No shipped behaviour changes, so no unit's version moves.
`meow-verbs evidence --keep format lint check test build` exits 0 on this
change's own tree, each result kept in `project/evidence/`, as the pull
request cites.

## Left alone

The code in `crates/meow/src/record.rs`, which meets REQ-1358.
