---
id: TSK-4980
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2535
closes: [REQ-0660, REQ-0662, REQ-0664]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Hold a document a task produces and the task to each other

A task names the document it produces in `produces:`, the document names the
task in `prompted-by:`, and `paw check` fails either side without the other,
as SPC-1070 states under "A document a task produces". One task, one branch, one pull request, one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture task with `produces: [RES-0002]` and `RES-0002` carrying `prompted-by: TSK-0001`, when `paw check` runs, then it reports nothing about the pair, and a task whose output is that document and no code is accepted (REQ-0660, REQ-0662). Closed by: a crate test naming REQ-0662, seen failing first.
2. Given the same task and a `RES-0002` with no `prompted-by:`, when `paw check` runs, then it reports a finding naming both artifacts, and the same for a `prompted-by:` whose task names no `produces:` (REQ-0662). Closed by: a crate test naming REQ-0662.
3. Given a produced `RES-0002` missing a section its kind requires, when `paw check` runs, then the shape check reports it as it would for a research record a step wrote (REQ-0664). Closed by: a crate test naming REQ-0664.

## What to do

Add `produces:` to `plugins/meow-flow/templates/task.md` as an optional field,
and `prompted-by:` as a field every kind accepts, in the layout. Add the
two-way check to the `record` feature of `crates/meow/`. Hold the template
change to SPC-1030 and the unit's `budget.toml`, and document both fields on
`plugins/meow-flow/README.md`.

## Depends on

- TSK-4970 (not blocking): a produced document may be of a declared kind, and the built-in kinds test the rule without one.

## Evidence

Not yet.

## Left alone

The relations index, which already derives the reverse direction and needs
no change for a field that cites upwards.
