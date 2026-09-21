---
id: TSK-1000
artifact: task
status: approved
revised: 2026-09-21
epic:
closes: []
issue: 3
---

# Plan the first decision: the reply shape

Planning is work, so it is a task, and this record is the one that authorises
the artifacts it merged with. It has no epic: no decision authorised it,
because it is the step that produces the first decision.

## What to do

Run steps 1 to 5 of the method over one slice of requirements, and produce the
preparatory pull request that closes issue #3:

- Choose the slice and state why one decision realises it completely.
- Write ADR-1000, allocated above the identifiers the deleted records held.
- Write SPC-1000 for the part the decision creates.
- Write EPC-1000 realising ADR-1000 entirely, with acceptance criteria taken
  from the decision before the tasks were written.
- Write one task record per task, and file a GitHub issue for each, only after
  the epic is approved.

## Depends on

No other task. This is the first turn of the cycle.

## Evidence

The artifacts themselves, merged in the preparatory pull request that closes
issue #3, and `tools/check_coverage.py` reporting that every requirement
ADR-1000 addresses lands in exactly one task.

## Left alone

No documentation in `docs/` was touched. Documenting is step 7 of the cycle and
belongs to the tasks that implement the decision, and this turn implements
nothing.

## What the method got wrong this turn

Written here because the cycle is a guess until it has run once.

- A specification describes the present, and the part it describes does not
  exist. REQ-0242 obliges the present tense, and step 3 writes the document
  before step 6 builds anything. SPC-1000 says as much in its scope and leaves
  `checked-at` empty, and the method has to settle which of the two readings it
  means.
- The templates cite an identifier scheme the record no longer uses:
  `templates/adr.md` and its neighbours cite `[R-H-043a]` and `R-AREA-nnn`,
  where the record allocates `REQ-NNNN`. Those citations resolve to nothing.
- The decision template carries no field for two things the method requires.
  REQ-2884 wants how anyone will know the decision was realised, and REQ-2886
  wants what it does not settle. ADR-1000 adds both as sections the template
  does not have.
