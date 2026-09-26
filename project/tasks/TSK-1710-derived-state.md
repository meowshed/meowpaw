---
id: TSK-1710
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1210
closes: [REQ-0527, REQ-0584, REQ-0591, REQ-0706, REQ-0712, REQ-0714]
issue: 282
---

# Show and status derive each requirement's state

Show and status derive each requirement's state, as ADR-1210 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a requirement closed by a done task in a verified epic, when `show` runs, then it prints the task and the verification. Closed by: a fixture.
2. Given a requirement no task closes, when `show` runs, then it prints "checked by nothing". Closed by: a fixture.
3. Given a verified epic with a finding on one of its tasks, when `status` runs, then it withholds "verified" and names the count. Closed by: a fixture.
4. Given a record outside any repository, when `status` runs, then it says the record is local to this machine. Closed by: a fixture.

## What to do

Make `show` print a requirement's derived state: each task closing it with its mark, and its epic's verification, or "checked by nothing". Make `status` count requirements by derived state, report an epic as verified only when `check` reports nothing on the epic, its decision or its tasks, and say the record is local to this machine where its root is under no version control.

## Depends on

Nothing. ADR-1210 is approved.

## Evidence

Four fixtures, each seen passing against the program and failing against a
stub that returns nothing. `show` on the fixture's requirement prints `verified` and the task done
in its epic, verified under `#1`, and a requirement no task closes prints
`checked by nothing`. `status` counts two requirements in force, one verified
and one checked by nothing. It prints `realised` for a verified epic, and
`drifted ... check reports 1 finding on it now` once a task of that epic links
to a missing file. It says the record is local to this machine once the
repository's `.git` is removed, and says nothing of it before. The state is
derived from the tasks' `closes`, their epics' marks and `checked-at`, and no
field stores it. Run on this repository's own record:

```text
$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 90 tests in 6.202s
OK

$ MEOW_METHOD_BIN=stub/meow-method python3 -m unittest discover -s plugins/meow-method/tests
FAILED (failures=87, errors=3)

$ meow-method status | tail -1
1075 in force: 411 verified, 5 closed and not yet verified, 30 in a task not yet done, 629 checked by nothing

$ meow-method show REQ-0704
...
State
  closed and not yet verified
  TSK-1700 done in EPC-1210, not yet verified
```

## Left alone

Reading tests that name a requirement, which ADR-1210 leaves.
