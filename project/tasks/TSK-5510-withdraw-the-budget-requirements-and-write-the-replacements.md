---
id: TSK-5510
artifact: task
status: done
revised: 2026-10-11
epic: EPC-2820
closes: [REQ-2748, REQ-5000, REQ-3194]
issue: 1102
projected: e5b72b7e2e2f
tracked: 521ff01b7e83
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Withdraw the budget requirements and write the replacements

The eight requirements stating the budget mechanism carry `status: withdrawn`,
each naming ADR-2970, and three requirements replace what survives them. One
task, one branch, one pull request, one review: the tests first, then the
change, its documentation and its marks.

## Acceptance criteria

1. Given REQ-1056, REQ-1057, REQ-1058, REQ-1072, REQ-1074, REQ-1676, REQ-3164
   and REQ-4120, when `paw check` reads them, then each carries `status:
withdrawn`, `revised: 2026-10-11`, and a body naming ADR-2970 as the
   decision that withdrew it, REQ-1676's naming REQ-5000 and REQ-3164's
   naming REQ-3194 as the replacements. Closed by: `paw check` and the
   requirements index, regenerated.
2. Given REQ-2748, REQ-5000 and REQ-3194, when `paw check` reads them, then
   all three carry `status: approved` in this pull request's commits, and
   each states one obligation: REQ-2748 that the harness states no size
   budget and reads none, REQ-5000 that the authoring capability enforces the
   writing standard on what it produces, REQ-3194 that a catalogue
   description states what the unit does for the reader. Closed by: `paw
check`, from the drafts.

## What to do

Withdraw by hand as `paw withdraw` states: change the `status:`, name the
decision and the replacement in the body, after the pattern REQ-2378 keeps.
REQ-2748, REQ-5000, REQ-3194 are already allocated and written as drafts.
Regenerate the requirements index with `paw index requirement --write`.

## Depends on

Nothing.

## Evidence

The eight requirements carry `status: withdrawn`, each naming ADR-2970 as the
decision that withdrew it, REQ-1676's naming REQ-5000 and REQ-3164's naming
REQ-3194 as the replacements (criterion 1), and `paw index requirement
--write` regenerated the index. REQ-2748, REQ-5000 and REQ-3194 carry
`status: approved`, and each states one obligation (criterion 2). `paw check`
reports no finding from this task's work.

## Left alone

The requirements that state the run bounds and the request budget, which
ADR-2970 leaves in force, and the frozen records that cite a budget.
