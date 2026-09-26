---
id: TSK-1830
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1250
closes: [REQ-3098, REQ-3180]
issue: 321
---

# An empty record reports its coverage as zero

An empty record reports its coverage as zero, as ADR-1250 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given an empty record, when `check coverage` and `status` run, then each says zero requirements and neither reads as complete. Closed by: a fixture.
2. Given REQ-3180, when its evidence is gathered, then the task records where each unit keeps what it keeps. Closed by: the evidence table.

## What to do

Make `check coverage` print how many requirements in force land in a task, `0 of 0` on an empty record, and make `status` say that an empty record's coverage is zero, not complete. Record the evidence that no unit writes into the repository to run itself.

## Depends on

Nothing. ADR-1250 is approved.

## Evidence

`check coverage` now states how many requirements in force land in a task
before its findings, and `status` says an empty record's coverage is zero. Two
fixtures, each seen passing against the program and failing against a stub
that returns nothing: a record with its requirements removed prints `coverage:
0 of 0 requirements in force land in a task; an empty record's coverage is
zero, not complete`, and `status` prints `none in force, so coverage is zero,
not complete`; the clean record prints `1 of 1`.

For REQ-3180, a search of the native tool for a file write finds 4
places. Two write a profile inside `profile.rs`'s tests, under `#[cfg(test)]`,
and the third is `index --write`, which writes the index a person asked for
and keeps nothing for the unit. No unit keeps state: every program is a binary
inside its unit's `bin/`, and no hook redirects output into the repository.

```text
$ meow-method check coverage
coverage: 480 of 1075 requirements in force land in a task
coverage: 0 findings

$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 108 tests in 7.422s
OK

$ MEOW_METHOD_BIN=stub/meow-method python3 -m unittest discover -s plugins/meow-method/tests
FAILED (failures=105, errors=3)
```

## Left alone

Onboarding from existing documents, which ADR-1250 leaves to the next
decision.
