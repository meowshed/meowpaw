---
id: TSK-4050
artifact: task
status: approved
revised: 2026-10-02
bug: BUG-1390
closes: []
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Refuse a start over an input of the wrong kind or a record file it can't read

`meow-loop start` exits 3 and creates no run directory where an input is the
wrong kind for the step, or where a Markdown file under the record root can't
be read, as SPC-1201's "Failure paths" now states. A run over such an input
could never finish and would spend its whole ceiling and budget, and a record
read as empty text is never guarded. One task, one branch, one pull request,
one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

Every check below lives in `plugins/meow-loop/tests/test_loop.py` and counts
what it matched, failing on a count of zero where one was expected.

1. Given an input of the wrong kind for each step that takes inputs
   (`requirements` over a requirement, `design` over a research record, `spec`
   and `epic` over a requirement, `implement` over a decision), when `start`
   runs, then it exits 3, prints `unresolved: <id>, a <kind>, is not a
<expected kind>, which a <step> run reads` and leaves no run directory.
   Closed by: `Step.test_wrong_kind_input_is_refused`.
2. Given an input of the right kind for each of the five steps, when `start`
   runs, then it makes no refusal on that account. Closed by:
   `Step.test_right_kind_input_is_not_refused`.
3. Given a Markdown file under the record root with its read permission
   removed, when `start` runs, then it exits 3, prints `unresolved: record
file <path> can't be read: <error>` and leaves no run directory. Closed by:
   `Step.test_unreadable_record_file_is_refused`.
4. Given this change's tree, when `meow-checks run format lint check test
build` runs, then each passes. Closed by: each verb's outcome in the task's
   pull request.

Each criterion is decidable from this task's own work.

## What to do

Add the two refusals to `start`'s checks of the inputs and the record root, as
SPC-1201's sections "The terms" and "Failure paths" state, and list each as a
row in the README's table of what `start` reports instead of a run. Read an
input's kind from the layout, as `paw ready` does, and add no refusal to
`paw ready`, because its exit status for a missing record isn't this task's
to change. Raise `meow-loop`'s minor version in `plugin.json`, and its
README's `describes:` with it, because `start` gains two refusals.

Write the checks first, in a commit of their own, and see them fail on main's
tree.

## Depends on

Nothing.

## Evidence

`python3 -m unittest plugins/meow-loop/tests/test_loop.py` exits 0 on this
change, reporting `Ran 101 tests` and `OK`. Three checks in `Step` close
criteria 1 to 3: `test_wrong_kind_input_is_refused`,
`test_right_kind_input_is_not_refused` and
`test_unreadable_record_file_is_refused`. The first and the third failed first
in the checks' own commit, where `start` made its call instead of refusing,
and the second passed there, as it guards that a right kind isn't refused.
Criterion 4 is closed by the five verbs' outcomes in this task's pull request,
since no run output is kept.

`wrong_kind` and `unreadable_files` in `crates/meow/src/record.rs` find the two
states, and `ready` in `crates/meow/src/runloop.rs` refuses on them before the
step's own readiness test. One older check changed in a commit of its own:
`Step.test_spec_run_over_no_requirement_never_finishes` no longer runs a
`spec` run over a requirement, which `start` now refuses, and the new check
covers that input.

## Left alone

`paw ready`, whose behaviour the `record` feature shares. The states
SPC-1201 now names that the runner already reports: a failed `git
check-ignore`, an unreadable profile and an unreadable layout.
