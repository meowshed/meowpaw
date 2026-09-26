---
id: TSK-1790
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1240
closes: [REQ-3020]
issue: 310
---

# The record can be counted before and after a migration

The record can be counted before and after a migration, as ADR-1240 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a record, when `count` runs twice, then it prints each kind's count by status and the identifiers, identical both times. Closed by: a fixture.

## What to do

Add `meow-method count`, printing each kind's number of artifacts by status and the number of distinct identifiers, in a fixed order.

## Depends on

Nothing. ADR-1240 is approved.

## Evidence

`meow-method count` prints each kind in the layout's order with its number of
artifacts by status, and the number of identifiers. A fixture withdraws the
fixture's requirement and sees `requirement: 1: 1 withdrawn`, the research
kind counted without its own index, `insight: 0`, and `identifiers: 8`, with
two runs printing the same text; it fails against a stub that returns nothing.
The read-only fixture now runs `count` too, and shows it writes nothing. Run on
this repository before the change lands:

```text
$ meow-method count
vision: 1: 1 live
specification: 11: 11 live
research: 131: 131 approved
requirement: 1080: 1075 approved, 5 withdrawn
decision: 25: 25 approved
epic: 25: 25 approved
task: 77: 77 approved
defect: 19: 19 approved
insight: 0
identifiers: 1369

$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 105 tests in 7.056s
OK

$ MEOW_METHOD_BIN=stub/meow-method python3 -m unittest discover -s plugins/meow-method/tests
FAILED (failures=102, errors=3)
```

## Left alone

A command that runs a migration, which ADR-1240 leaves.
