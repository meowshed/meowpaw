---
id: TSK-2180
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1420
closes:
  [
    REQ-0356,
    REQ-0358,
    REQ-0360,
    REQ-0362,
    REQ-0364,
    REQ-0368,
    REQ-0370,
    REQ-0372,
  ]
issue: 476
projected: ffc44f4fce39
---

# `paw check` holds a defect's triage, reproduction and closing

`paw check` reports a defect missing what ADR-1440 requires of its triage,
reproduction and closing, an epic for a defect that doesn't need one, and a
`prompted-by` naming no defect, with the rules new to approved defects
applying to drafts. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given draft defects breaking each rule, when `paw check` runs, then it
   reports each: a written Triage and no `enters`; `enters` of `implement`
   or `design` with no `violates`;
   `enters` with an empty Reproduction; `rejected` with an empty Triage; all
   tasks done with an empty Closed by; no `severity`. Closed by: fixtures, one
   per rule, naming its requirement, seen failing first.
2. Given an epic realising a defect with one task, or with two and no order
   between them, when `paw check` runs, then it reports the epic. Closed by: a
   fixture naming REQ-0356.
3. Given a requirement with `prompted-by` naming a decision, when `paw check`
   runs, then it reports that `prompted-by` names no defect. Closed by: a
   fixture naming REQ-0362.
4. Given this repository's record, whose defects were approved before this
   decision, when `paw check` runs, then it reports nothing. Closed by: its
   output.

## What to do

Add `enters` to the defect kind, with the nine steps as its values, and the
rules above to the layout and the record's program: requiring `enters` as a
draft rule, the others as rules. Add `enters` to the defect
template, and describe the rules in `meow-flow`'s page.

## Depends on

TSK-2170, because the rules read the `bug` field and the defect's tasks it
adds.

## Evidence

The defect kind gains `enters`, checked against the nine steps, and the
record's program holds the rules ADR-1440 lists: `enters-after-triage` as a
draft rule, and `enters-fits`, `rejected-says-why` and `closed-names-check` as
rules on every defect. An epic carries `defect-epic-ordered`, and research, a
requirement and a decision carry `prompted-by-defect`. Severity was already a
required field. The defect template carries `enters`, and `meow-flow`'s page
describes the rules.

Seven fixtures in `Triage`, each naming its requirement, failed against
`main`'s `paw` and pass against this one. The eighth, severity, passed on both
and stands as a regression check. This repository's record, whose defects were
approved before ADR-1440, reports nothing:

```text
$ MEOW_FLOW_BIN=<main's paw> python3 -m unittest ... -k Triage
FAILED (7 failures)
$ python3 -m unittest discover -s plugins/meow-flow/tests
OK
$ plugins/meow-flow/bin/paw check
rules: 0 findings
$ plugins/meow-verbs/bin/meow-verbs run format lint test
summary: format passed, lint passed, test passed
```

## Left alone

The step files, which TSK-2190 changes.
