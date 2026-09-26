---
id: EPC-1070
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1100
checked-at:
---

# The record, checked by a unit the harness ships

Realises exactly one authorising record, ADR-1100, as this epic amends it. The
epic is complete when `meow-method check` checks a repository's record where
the repository declares it, reports every finding and changes nothing, and
this repository's `test` verb runs it in place of the record scripts in
`tools/`.

## Acceptance criteria

Taken from ADR-1100, from its list of how I will know it was realised, before
the tasks below were written, with criteria 4 and 5 counting the four scripts
that check the record, as the amendment on ADR-1100 states:

1. Each check reports a planted defect in a scratch record, with the file and
   the line, and reports nothing on a clean record.
2. With `root` pointing outside the repository, the checks read the record
   there.
3. The program changes no file: the tree is identical before and after a run.
4. On this repository, `meow-method check` reports what the four scripts it
   replaces report at the same revision, and nothing else.
5. Those four scripts are gone, and this repository's `test` verb runs
   `meow-method check` and passes.
6. Every requirement ADR-1100 addresses lands in exactly one closed task, and
   the checks over the record report nothing outstanding.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1330 `plugins/meow-method/`: the program, the layout as data
      and a fixture per check, each seen failing first, and the parity run
      against the four scripts
      closes: REQ-0137, REQ-0145, REQ-0246, REQ-0520, REQ-0521, REQ-0524,
      REQ-0573, REQ-0590, REQ-0656
      evidence: eighteen fixtures, each seen failing against a stub, and the
      parity run at one revision, in #144.
      depends: TSK-1350 of EPC-1080 - ADR-1110 builds the program in the
      native tool, whose crate that task creates

- [x] T-002 TSK-1340 this repository on the unit: `[record]`, the `test` verb,
      the four scripts deleted, `CLAUDE.md`, the page, the budget and the
      marketplace entry
      closes: REQ-1673
      evidence: `meow-verbs run test` passing with `meow-method check` in it,
      and no reference to the four scripts outside the record, in #145.
      depends: TSK-1330 - the verb runs the program, and parity has to hold
      before the scripts go

## Coverage

ADR-1100 addresses ten requirements. Each lands in exactly one task above,
and `tools/check_coverage.py`, and after T-002 `meow-method check coverage`,
compares the decision's `addresses` against the union of the tasks' `closes`.

T-001 alone tests the decision on scratch records and on this one. T-002 is
the point where this repository stops depending on scripts the harness
doesn't ship.

## Not covered

Nothing ADR-1100 addresses is left out. Declared kinds, transitive coverage,
suspect citations and orphaned artifacts are outside this epic.
