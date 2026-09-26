---
id: TSK-1420
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1100
closes:
  [
    REQ-0198,
    REQ-0200,
    REQ-0206,
    REQ-0210,
    REQ-0212,
    REQ-0228,
    REQ-0240,
    REQ-0294,
    REQ-0302,
    REQ-0321,
  ]
issue: 189
---

# The chain's state, a step's gate and the template in force

One task, one branch, one pull request, one review.

## What to do

Add `status`, `ready` and `template` to `meow record`, as SPC-1090 states them. `ready <step> <id>...` checks the step's input against the table in SPC-1090 and exits 0, 1 naming each missing or unapproved input, or 2 for an unknown step. `status` prints the drafts waiting for approval first, then each approved decision's step and next step. `template <kind>` prints the path of the template in force. Write a fixture for each of the nine gates, one for the state, one showing `status` prints the same text twice, and one for each failure path, each seen failing first against a program that returns nothing.

## Depends on

Nothing. ADR-1130 and SPC-1090 are approved.

## Evidence

`meow record` gains `status`, `ready` and `template` as SPC-1090 states them.
Fourteen new fixtures cover each gate, the state and each failure path. Three
fixtures, one of them older, passed against a program that returns nothing,
so each now asserts the program's output, and every fixture fails against it:

```text
$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 34 tests
OK

$ MEOW_METHOD_BIN=stub/meow-method python3 -m unittest discover -s plugins/meow-method/tests
FAILED (failures=33, errors=1)
```

Run on this repository, `status` leads with four tasks still stored as
`draft` and places each decision, and `ready` refuses TSK-1430 until
TSK-1420 is done:

```text
$ meow-method ready implement TSK-1430
meow-method ready implement: not ready
  TSK-1420, which TSK-1430 depends on, isn't done
```

`status` also shows ADR-1030, ADR-1040 and ADR-1060 with no epic of their own,
which REQ-0239 requires, and EPC-1030 with every task done and no
verification. Those are defects in the record, not in the program, and a
defect record carries them.

## Left alone

The skill that calls these, which TSK-1440 writes.
