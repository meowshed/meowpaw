---
id: BUG-1300
artifact: bug
status: approved
severity: minor
violates: REQ-1358
enters: cover
found: 2026-09-29
revised: 2026-09-29
issue: 679
---

# No check shows `paw status` waiting on a blocking dependency

No fixture shows `paw status` passing over a task whose dependency blocks, so
a `status` that ignores dependencies altogether passes the suite, and
REQ-1358's `status` half is guarded by nothing.

## Reproduction

`main` after #673, with `meow-flow` 0.39.1 built by `crates/meow/build-units`.

1. In `crates/meow/src/record.rs`, in the `doable` search `paw status` runs,
   replace
   `.map(|doc| depends_on(doc).iter().all(|d| task_finished(known, d)))` with
   `.map(|_doc| true)`, and rebuild.
2. Run `python3 -m unittest test_record` in `plugins/meow-flow/tests`.

## What the system does

Every fixture in the class `Dependencies` passes against that build, as it
does against the unchanged one. The only `status` fixture,
`test_status_names_a_task_whose_only_dependency_does_not_block`, lists
TSK-0002 first in the epic and asserts that `status` names TSK-0002, which a
`status` reading no dependency names too.

Three `dependency-declared` fixtures, `test_a_declared_dependency_passes`,
`test_a_bare_dependency_in_a_draft_is_reported` and
`test_a_line_naming_two_tasks_is_reported`, match only `file:line:` and never
the rule's message. So a report of that line by any rule passes them. No other
rule reports those lines today, so this half is a gap and not yet a false
pass.

## What it should do, and why

A `status` that stops waiting on a blocking dependency should fail a fixture,
because REQ-1358 asks `paw` to wait only on a blocking line, and EPC-1710's
verification cites the `Dependencies` fixtures as the check that it does. The
fixture should hold the contrast: the same epic, with the line marked
`(blocking)` or left bare on an approved task, makes `status` pass over
TSK-0002 and name TSK-0001. Each `dependency-declared` fixture should match
the rule's message on the reported line, so the line is shown reported by
that rule.

## Triage

It enters at cover, because the code meets REQ-1358 and the task's checks
miss half of what the requirement asks: `ready cover` and `ready implement`
are checked in both directions, and `status` in one. Minor, because nothing
is broken today, and the gap lets a later change break `status` unnoticed.

## Closed by

`Dependencies.test_status_waits_on_a_blocking_dependency` in
`plugins/meow-flow/tests/test_record.py`, failing against the build in the
reproduction, and the three `dependency-declared` fixtures asserting the
rule's message.

## Tasks

- [x] T-001 TSK-2920 show `status` waiting on a blocking dependency, in
      `plugins/meow-flow/tests/test_record.py`
      evidence: 2 checks seen failing against the reproduction's build, 213
      `meow-flow` record fixtures passing, in #680.
