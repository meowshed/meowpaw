---
id: TSK-1570
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1160
closes:
  [
    REQ-0304,
    REQ-0306,
    REQ-0308,
    REQ-0310,
    REQ-0311,
    REQ-0312,
    REQ-0313,
    REQ-0314,
    REQ-0315,
    REQ-0316,
    REQ-0318,
    REQ-0320,
    REQ-0322,
    REQ-0324,
    REQ-0326,
    REQ-0544,
    REQ-3108,
  ]
issue: 227
---

# The review step carries its obligations

One task, one branch, one pull request, one review.

## What to do

Write each obligation the requirements below place on review into `steps/review.md` as a labelled rule, with its reason in the same sentence, naming no requirement identifier, because the file ships to other repositories. Keep the five-tag vocabulary the prompt check holds. Record, under Evidence, a table mapping each requirement this task closes to the label of the rule that carries it, and show the prompt check and `meow-method check` passing.

## Depends on

Nothing. ADR-1160 and SPC-1090 are approved.

## Evidence

Each requirement this task closes is carried by a labelled rule in the step
file named, and every rule names no requirement, because the file ships to
other repositories:

| Requirement | Carried by              |
| ----------- | ----------------------- |
| REQ-0304    | W1 in `steps/review.md` |
| REQ-0306    | W8 in `steps/review.md` |
| REQ-0308    | W8 in `steps/review.md` |
| REQ-0310    | W1 in `steps/review.md` |
| REQ-0311    | W2 in `steps/review.md` |
| REQ-0312    | W4 in `steps/review.md` |
| REQ-0313    | W3 in `steps/review.md` |
| REQ-0314    | W4 in `steps/review.md` |
| REQ-0315    | W9 in `steps/review.md` |
| REQ-0316    | W6 in `steps/review.md` |
| REQ-0318    | W6 in `steps/review.md` |
| REQ-0320    | W7 in `steps/review.md` |
| REQ-0322    | W5 in `steps/review.md` |
| REQ-0324    | W5 in `steps/review.md` |
| REQ-0326    | W1 in `steps/review.md` |
| REQ-0544    | W9 in `steps/review.md` |
| REQ-3108    | W5 in `steps/review.md` |

The prompt check passes on the step files and `meow-method check` reports 0
findings, as the gate below shows. Whether the model follows the rules is
measured by evaluation, which is postponed.

## Left alone

Measuring whether the model follows the rules, which waits for evaluation.
