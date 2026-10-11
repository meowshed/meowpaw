---
id: TSK-5550
artifact: task
status: done
revised: 2026-10-11
epic: EPC-2820
closes: []
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Update the documentation and the specs that state a budget

The living specifications and the constitution lose their budget and token
statements, so the record says what the tree now does. This task runs last and
runs the gate.

## Acceptance criteria

1. Given `project/specs/` and `CLAUDE.md`, when `grep` looks for
   `budget.toml`, `permanent_characters` and the gate's `budget` row, then
   only the withdrawn-requirement bodies and frozen records match. Closed by:
   `grep` in the pull request.
2. Given the changed tree, when `mise run all` runs, then it passes as far as
   its pre-existing findings allow, and `paw check` reports no finding this
   epic's change introduced. Closed by: the gate's output in the pull request.

## What to do

SPC-1030: the budget section, the `meow-author cost` table row and the
overrun rows go, keeping the load-on-demand rules. SPC-1020: covered by
TSK-5540. SPC-1080: the `author` table's `determines` and `by_hand` lines.
SPC-1010: the overrun table row. SPC-1110: the ceiling paragraphs and the
finding. SPC-1130, SPC-1201: the `budget.toml` table rows. SPC-1300: the
`budget.toml` lines in the layout, the package section and the manifest
list. CLAUDE.md: the gate table's `budget` row.

## Depends on

- TSK-5520 (blocking): the gate runs only once the budget task is gone from
  it.

## Evidence

SPC-1030's Size section states REQ-2748 and REQ-5000 and the platform cap;
SPC-1010, SPC-1020, SPC-1080's table, SPC-1110, SPC-1130, SPC-1201 and
SPC-1300 lost their budget and token statements, and CLAUDE.md's gate table
lost the `budget` row (criterion 1). `paw check` reports only the two
findings `main` reports, SPC-1300 resting on the withdrawn REQ-4110 and the
requirements named by no task, and `mise run all` fails only where `main`'s
does, its `test-record` task (criterion 2).

## Left alone

The frozen records, and the documentation of the request budget and the run
bounds.
