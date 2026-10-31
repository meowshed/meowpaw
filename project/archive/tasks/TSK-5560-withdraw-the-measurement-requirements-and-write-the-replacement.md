---
id: TSK-5560
artifact: task
status: done
revised: 2026-10-11
epic: EPC-2830
closes: [REQ-2750, REQ-5100]
issue: 1107
projected: 0f454a986ef0
tracked: 61dd85c08a24
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Withdraw the measurement requirements and write the replacements

The twenty requirements that make prompt evaluation obligatory carry `status:
withdrawn`, each naming ADR-2980; REQ-2750 replaces REQ-1078's surviving
obligation, and REQ-5100 replaces the workflow prohibition REQ-3035 carried. One task, one branch, one pull request, one review: the tests
first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given REQ-0153, REQ-0159, REQ-0160, REQ-0956, REQ-1078, REQ-1150,
   REQ-1759, REQ-3022, REQ-3024, REQ-3026, REQ-3028, REQ-3030, REQ-3032,
   REQ-3035, REQ-3036, REQ-3038, REQ-4124, REQ-4800, REQ-4802 and REQ-4804,
   when `paw check` reads them, then each carries `status: withdrawn`,
   `revised: 2026-10-11`, and a body naming ADR-2980 as the decision that
   withdrew it. Closed by: `paw check` and the requirements index,
   regenerated.
2. Given REQ-2750 and REQ-5100, when `paw check` reads them, then both carry
   `status: approved` in this pull request's commits, and each states one
   obligation: REQ-2750 the reviewed move, REQ-5100 the workflow prohibition.
   Closed by: `paw check`, from the drafts.

## What to do

Withdraw by hand as `paw withdraw` states: change the `status:`, name the
decision and any replacement in the body, after the pattern REQ-2378 keeps.
REQ-2750 and REQ-5100 are allocated and written as drafts. Regenerate the requirements
index with `paw index requirement --write`.

## Depends on

Nothing.

## Evidence

The twenty requirements carry `status: withdrawn`, each naming ADR-2980 as
the decision that withdrew them (criterion 1), and the requirements index is
regenerated. REQ-2750 and REQ-5100 carry `status: approved`, each stating one
obligation, the reviewed move and the workflow prohibition (criterion 2).
`paw check` reports no finding from this task's work.

## Left alone

The requirements whose subject is checkability or the verification kinds
(REQ-1662, REQ-1664, REQ-2076), the prose gate's REQ-3752, and the frozen
records citing a measurement.
