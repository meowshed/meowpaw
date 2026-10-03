---
id: TSK-4060
artifact: task
status: approved
revised: 2026-10-03
realises: ADR-2350
closes: [REQ-3004]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Stop naming the step that took a retired step's work

`paw ready` refuses `cover`, `document` and `verify` as any other name it
doesn't know, with exit 2 and the seven steps, as SPC-1090 now states. One
task, one branch, one pull request, one review: the tests first, then the
change, its documentation and its marks.

## Acceptance criteria

1. Given `paw ready cover TSK-0001`, `document` and `verify`, when each runs,
   then each exits 2 and prints `paw ready: no step is named <name>; the steps
are research, requirements, design, spec, epic, implement, review`, and
   prints no replacement. Closed by:
   `test_a_retired_step_is_an_unknown_step` in
   `plugins/meow-flow/tests/test_record.py`, which replaces
   `test_a_retired_step_names_what_replaced_it`.
2. Given an approved defect whose `enters` names `cover`, when `paw check`
   runs, then it reports no finding on `enters`. Closed by:
   `test_a_defect_may_enter_at_cover`, which already holds it and stays.
3. Given `plugins/meow-flow/README.md`, when it is read, then no sentence says
   `paw ready` names the step that took a retired step's work. Closed by:
   judgement, because the page is prose read by a person, and the reviewer
   searches it for "for one release".
4. Given this change's tree, when `meow-checks run format lint check test
build` runs, then each passes. Closed by: each verb's outcome in the
   task's pull request.

## What to do

Remove the refusal from `ready` in `crates/meow/src/record.rs`, keep the list
of the three names for the `enters` rule alone, and say so in its comment. Drop
the sentence from the unit's README. Raise `meow-flow`'s patch version in
`plugin.json` and the README's `describes:` with it.

Write the checks first, in a commit of their own, and see them fail.

## Depends on

Nothing.

## Evidence

Not yet. This line stays first until every verb has passed.

## Left alone

The `enters` rule's acceptance of a retired step in an approved defect, which
ADR-2350 keeps. The `meow-verbs` stub.
