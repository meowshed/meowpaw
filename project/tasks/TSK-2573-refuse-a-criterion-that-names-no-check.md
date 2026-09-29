---
id: TSK-2573
artifact: task
status: approved
revised: 2026-09-29
bug: BUG-1263
closes: []
issue: 676
---

# Refuse a criterion that names no check and isn't under Judgement

`paw ready implement` refuses a Cover that leaves out of `Judgement` a
criterion with no `Closed by:` line, whatever `Checks` names, and a
`Judgement` entry whose reason holds no letter. So every criterion either
names the evidence that closes it or is named as resting on judgement, with a
reason, before the implementation starts. One task, one branch, one pull
request, one review.

## Acceptance criteria

1. Given an approved open task whose criterion 1 carries a `Closed by:` line
   and whose criteria 2 and 3 carry none, with a Cover whose `Checks` names a
   file and whose `Judgement` reads `none`, when `paw ready implement` runs,
   then it exits 1 with a line naming criterion 2 and a line naming criterion
   3, and no line naming criterion 1. Closed by:
   `CoverClosedBy.test_a_criterion_naming_no_check_is_named_under_judgement`
   in `plugins/meow-flow/tests/test_record.py`.
2. Given the same task with `Judgement: 2: .; 3: -`, when
   `paw ready implement` runs, then it exits 1 naming criteria 2 and 3 as
   having no reason. Closed by:
   `CoverClosedBy.test_a_reason_with_no_letter_is_no_reason`.
3. Given the same task with `Judgement: 2: a reader decides; 3: a reader
decides`, when `paw ready implement` runs, then it exits 0. Closed by:
   `CoverClosedBy.test_every_criterion_named_or_closed_is_ready`.

## What to do

In `cover_gaps` in `crates/meow/src/record.rs`, read each numbered criterion
under `## Acceptance criteria` with the lines that continue it, up to the next
numbered criterion. Refuse each criterion that has no `Closed by:` with text
after it and isn't named under `Judgement`, naming the criterion, and refuse a
`Judgement` reason with no letter as a reason left out. Keep BUG-1261's rules.
State the rule in SPC-1090's section "The gate", and say in
`steps/cover.md` rule C2 that the gate refuses such a criterion.

Give the fixtures' criteria the `Closed by:` lines the template asks for, so
the other Cover checks keep exercising a Cover that passes. Raise
`meow-flow`'s patch version. Write the checks first, in a commit of their own,
and see them fail.

## Depends on

Nothing. BUG-1263 is approved.

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

Whether the evidence a `Closed by:` line names can settle its criterion, and
whether a reason with letters in it is a good one: no program reads either,
so the cover step's instructions and the review hold them. The link between a
`Closed by:` line and a path under `Checks`, because the tasks in this record
close criteria by a class name, a kept run or a fixture left unchanged, none
of which is a path `Checks` lists.
