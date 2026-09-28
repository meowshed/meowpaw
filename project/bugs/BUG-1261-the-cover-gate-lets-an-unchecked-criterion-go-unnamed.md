---
id: BUG-1261
artifact: bug
status: approved
severity: major
violates: REQ-3216
enters: design
found: 2026-09-28
revised: 2026-09-28
issue: 650
---

# `paw ready implement` accepts a Cover that leaves a criterion nothing checks unnamed

`paw ready implement` exits 0 on Covers under which a criterion that no check
covers is never named under `Judgement`. So the criterion reads as covered
while nothing covers it, which is what REQ-3216 exists to prevent.

## Reproduction

`main` after #647, with `meow-flow` 0.35.0 built by `crates/meow/build-units`.

1. Take the fixture record in `plugins/meow-flow/tests/test_record.py`: an
   approved epic and an approved open task, TSK-0001, whose
   `## Acceptance criteria` holds `1.` and `2.`, with `tests/t.py` and
   `evidence/run.txt` present.
2. Give it each of these Covers in turn, and run
   `paw ready implement TSK-0001` after each:
   - `Checks: none`, `Failing run: evidence/run.txt`, `Landed in: #1`,
     `Judgement: none`;
   - every line `none`, with the criteria written as bullets and not
     numbered;
   - `Checks: tests/t.py`, the run and `#1` named, and
     `Judgement: 7: a reason`;
   - the same, with `Judgement:` left empty;
   - every line `none`, on a task with no `## Acceptance criteria` section.

## What the system does

Each of the five runs exits 0 and prints
`paw ready implement: ready; TSK-0001 approved and complete`. `cover_gaps` in
`crates/meow/src/record.rs` follows the filled rule ADR-1620 states: it asks
`Judgement` to name every criterion only when `Checks`, `Failing run` and
`Landed in` all read `none`. It counts only criteria numbered `1.`, never
compares a `Judgement` number with the criteria, and reads an empty value as
`none`.

## What it should do, and why

A Cover with `Checks: none` checks nothing, so every criterion rests on
judgement and `Judgement` names each one, whatever `Failing run` and
`Landed in` say. A task with no numbered criterion has nothing a Cover can
name, so the gate refuses it. A `Judgement` number that matches no criterion
names nothing, so the gate refuses it too. A Cover line left empty says
neither what it holds nor `none`, so the gate asks for one of the two. Each
refusal names the criterion, the number or the line.

REQ-3216 asks that a criterion no program can check is named as resting on
judgement, with its reason, before the implementation starts. Each of the five
Covers above lets an implementation start with such a criterion unnamed.

Where `Checks` names a check, the program can't tell which of the remaining
criteria no program can check, so that case stays with the cover step's
instructions, `steps/cover.md`, and outside this defect.

## Triage

It enters at design, because REQ-3216 is right and ADR-1620's filled rule is
too weak to hold it: the program implements the rule as written. ADR-1620 is
approved and frozen, so this record states the corrected rule, and SPC-1090's
section "The gate" carries it. Major, because the gate that holds REQ-3216
passes the very Cover the requirement forbids.

## Closed by

The reproduction as fixtures in the class `CoverCriteria` in
`plugins/meow-flow/tests/test_record.py`, one for each of the five Covers,
each refused naming what is missing.

## Tasks

- [x] T-001 TSK-2571 refuse a Cover that leaves a criterion nothing checks
      unnamed, in `crates/meow/src/record.rs`
      evidence: 5 checks seen failing first, 190 `meow-flow` fixtures
      passing, in #653.
