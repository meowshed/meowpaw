---
id: TSK-1700
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1210
closes: [REQ-0704, REQ-0710]
issue: 281
---

# The check reports work left unmarked and identifiers that resolve to nothing

The check reports work left unmarked and identifiers that resolve to nothing, as ADR-1210 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a task with evidence and an epic marking it `[ ]`, when `check coverage` runs, then it reports the task. Closed by: a fixture.
2. Given a task closing a withdrawn requirement in an unverified epic, when `check coverage` runs, then it reports the task. Closed by: a fixture.
3. Given a body naming an identifier with no file, when `check relations` runs, then it reports the line. Closed by: a fixture.

## What to do

In `check coverage`, report a task whose Evidence section holds more than "Not yet." while its epic marks it `[ ]`, and a task closing a withdrawn requirement in an epic with no `checked-at`. In `check relations`, scan each record's body for identifiers of a known kind and report one with no file. Fix what the new findings report in this repository's own record in the same change.

## Depends on

Nothing. ADR-1210 is approved.

## Evidence

Three fixtures, each seen passing against the program and failing against a
stub that returns nothing. `check coverage` reports a task whose Evidence
section opens with anything but "Not yet." while its epic marks it `[ ]`, and
passes once the section opens with "Not yet." and a postponement note. It
reports a task closing a withdrawn requirement while its epic has no
`checked-at`, and passes once the epic is verified. `check relations` reports
`ADR-0009` in a draft's prose, ignores one in a code span and one in a fence,
and passes once the task is approved.

Two findings changed the design. Scanning every body found ten identifiers in
approved records that resolve to nothing on purpose, such as BUG-1110 naming
the research nobody wrote, so the scan reads drafts alone, and ADR-1210 carries
the amendment. The first version of the unmarked check reported TSK-1260,
which the owner postponed and whose Evidence section opens with "Not yet."
above the note, so the check now matches a claim of done and not any text.

```text
$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 86 tests in 5.568s
OK

$ MEOW_METHOD_BIN=stub/meow-method python3 -m unittest discover -s plugins/meow-method/tests
FAILED (failures=83, errors=3)

$ meow-method check coverage; meow-method check relations
coverage: 0 findings
relations: 0 findings
```

## Left alone

Reading tests that name a requirement, which ADR-1210 leaves.
