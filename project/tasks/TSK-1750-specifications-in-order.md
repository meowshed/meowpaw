---
id: TSK-1750
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1230
closes: [REQ-0525]
issue: 299
---

# The specifications read in citation order

The specifications read in citation order, as ADR-1230 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given an index listing a specification before one it cites, when `check index` runs, then it reports the pair. Closed by: a fixture.
2. Given this repository, when `check index` runs, then it reports nothing. Closed by: the check's output.

## What to do

In `check index`, for a living kind with a prefix, read the order in which its index first names each of its documents, and report a document named before one it cites. Remove the unit specifications' identifiers from SPC-1020, SPC-1030 and SPC-1080, naming the unit instead, and reorder the specifications in `project/README.md` so the check passes.

## Depends on

Nothing. ADR-1230 is approved.

## Evidence

`check index` now reads a living kind's index as its reading order, and
reports a document listed before one it cites. A fixture lists a specification
before the one it builds on and sees the finding at its line, then swaps the
two and sees `index: 0 findings`; it fails against a stub that returns nothing.

This repository failed the check before the change: SPC-1010 was listed before
SPC-1020 and SPC-1030, and SPC-1040 to SPC-1070 before SPC-1080, in two cycles.
The contracts SPC-1020 and SPC-1030 no longer name a unit's specification, and
SPC-1080 no longer names the units' specifications that cite it, which breaks
both cycles. The index now reads SPC-1000, SPC-1020, SPC-1030, SPC-1010,
SPC-1080, SPC-1040, SPC-1050, SPC-1060, SPC-1070, SPC-1090 and SPC-1100.

```text
$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 96 tests in 6.295s
OK

$ MEOW_METHOD_BIN=stub/meow-method python3 -m unittest discover -s plugins/meow-method/tests
FAILED (failures=93, errors=3)

$ meow-method check index
index: 0 findings
```

## Left alone

Splitting approved requirements that carry two obligations, which ADR-1230
leaves to the amendment path.
