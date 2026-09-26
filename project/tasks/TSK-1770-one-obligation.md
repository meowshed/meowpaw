---
id: TSK-1770
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1230
closes: [REQ-2880]
issue: 301
---

# A draft requirement carries one obligation, stands alone, and prohibits with MUST NOT

A draft requirement carries one obligation, stands alone, and prohibits with MUST NOT, as ADR-1230 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a draft requirement with two keywords, one leaning on a neighbour, and one negating a requirement, when `check rules` runs, then it reports each. Closed by: a fixture.
2. Given the same statements in an approved requirement, when `check rules` runs, then it reports nothing. Closed by: a fixture.

## What to do

Add the draft rules `one-obligation`, `stands-alone` and `no-negated-requirement` for the requirement kind, reading the paragraph under the heading.

## Depends on

Nothing. ADR-1230 is approved.

## Evidence

Four fixtures, each seen passing against the program and failing against a
stub that returns nothing. On a draft requirement, `check rules` reports "The
check MUST run and MUST NOT write." as carrying two keywords, naming both,
and passes "The check MUST NOT write."; it reports "Such a record MUST be
kept." as leaning on a neighbour, and "No step MUST write." as negating a
requirement. The same three statements in an approved requirement report
nothing, because an approved requirement keeps the rules it was approved
under. This repository reports `rules: 0 findings`, since no requirement is a draft.

```text
$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 102 tests in 6.761s
OK

$ MEOW_METHOD_BIN=stub/meow-method python3 -m unittest discover -s plugins/meow-method/tests
FAILED (failures=99, errors=3)
```

## Left alone

Splitting approved requirements that carry two obligations, which ADR-1230
leaves to the amendment path.
