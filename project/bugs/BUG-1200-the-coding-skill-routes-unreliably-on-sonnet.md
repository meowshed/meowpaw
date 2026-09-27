---
id: BUG-1200
artifact: bug
status: approved
severity: major
violates: REQ-2010
found: 2026-09-27
revised: 2026-09-27
issue: 465
---

# `meow-code:change` loads before an edit in two of five Sonnet 5 sessions

## Reproduction

With `meow-code` 0.1.0 on Claude Code 2.1.280, on `main` after #463, in a
scratch repository holding one shell function, with only this unit installed,
each session asked "In count.sh, make count print 2 instead of 1.":

```text
claude-sonnet-5, 5 runs: loaded 2, missed 3 (Read -> Edit, no skill)
claude-opus-5-5, 5 runs: loaded 5
```

## What the system does

On Sonnet 5 the model often reads the file and edits it without loading the
skill, so none of the unit's rules are in front of it for that change. The
description said the skill loads before any code is written, edited,
refactored or deleted, but named no small case and didn't forbid skipping it.
One session in TSK-2150's evidence loaded it, which was luck and not a
measure.

## What it should do, and why

The skill carries REQ-2010 and every other rule ADR-1420 lists, and those
rules hold only when the skill is loaded before the edit. ADR-1420's criterion
3 asks that it load before the first edit on both models. `violates` names
REQ-2010 as the first rule a missed load drops; every rule of the skill is
dropped with it.

## Triage

Implementation: the description, which routes the skill. Major, because the
unit does nothing in three sessions of five on the model most sessions run.

## Closed by

A description naming the one-line case and forbidding the skip, shaped like
the writing skill's, which ADR-1050 measured. Measured on the same prompt with
only the unit installed:

```text
claude-sonnet-5, 10 runs: loaded 10
claude-opus-5-5, 5 runs: loaded 5
a question changing nothing, 3 runs per model: loaded 0 of 6
```

The description costs 274 characters, within the unit's ceiling of 330, and
`meow-code` moves to 0.1.1. The measurement is by hand, as the repository's
evaluations are, and the verification of EPC-1400 repeats it.
