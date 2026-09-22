---
id: TSK-1100
artifact: task
status: approved
revised: 2026-09-22
epic:
closes: []
issue: 46
---

# Plan the second decision: the writing standard

Planning is work, so it is a task, and this record authorises the artifacts it
merges with. It has no epic, because it is the step that produces the decision
an epic would realise.

## What to do

Run steps 1 to 5 of the method over one slice of requirements, and produce the
preparatory pull request that closes issue #46:

- Choose the slice and state why one decision realises it completely.
- Withdraw the requirements the slice contradicts and write their
  replacements, under issue #47: REQ-0020 for REQ-3178 and REQ-3180, and
  REQ-1004 and REQ-1006 for REQ-3184 and REQ-3186.
- Write ADR-1010, and bring the vision and `CLAUDE.md` into line with it.
- Write SPC-1010 for the standard and SPC-1020 for measuring the harness.
- Write EPC-1010 realising ADR-1010 entirely, with acceptance criteria taken
  from the decision before the tasks were written.
- Write one task record per task, TSK-1110 to TSK-1210, and file an issue for
  each only after the epic is approved (REQ-1352).

## Depends on

EPC-1000, closed at #27. The measurement it produced found that three cases of
four cannot discriminate, which is why repairing the case set is part of this
slice.

## Evidence

Not yet. The task closes on the preparatory pull request merging, with
`tools/check_coverage.py` reporting that every requirement ADR-1010 addresses
lands in exactly one task, and the other checks over the record passing.

## Left alone

No documentation in `docs/` was touched. Documenting is step 7 of the cycle and
belongs to the tasks that implement the decision, and this turn implements
nothing.
