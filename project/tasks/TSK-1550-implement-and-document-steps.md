---
id: TSK-1550
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1160
closes:
  [
    REQ-0257,
    REQ-0259,
    REQ-0267,
    REQ-0269,
    REQ-0272,
    REQ-0274,
    REQ-0276,
    REQ-0290,
    REQ-0292,
    REQ-0298,
    REQ-0300,
    REQ-0450,
    REQ-0458,
    REQ-0460,
    REQ-0462,
    REQ-0464,
    REQ-0466,
    REQ-2774,
    REQ-3104,
  ]
issue: 225
---

# The implement and document steps carry their obligations

One task, one branch, one pull request, one review.

## What to do

Write each obligation the requirements below place on implement and document into `steps/implement.md`, `steps/document.md` as a labelled rule, with its reason in the same sentence, naming no requirement identifier, because the file ships to other repositories. Keep the five-tag vocabulary the prompt check holds. Record, under Evidence, a table mapping each requirement this task closes to the label of the rule that carries it, and show the prompt check and `meow-method check` passing.

## Depends on

Nothing. ADR-1160 and SPC-1090 are approved.

## Evidence

Each requirement this task closes is carried by a labelled rule in the step
file named, and every rule names no requirement, because the file ships to
other repositories:

| Requirement | Carried by                  |
| ----------- | --------------------------- |
| REQ-0257    | I5 in `steps/implement.md`  |
| REQ-0259    | I4 in `steps/implement.md`  |
| REQ-0267    | I1 in `steps/implement.md`  |
| REQ-0269    | I2 in `steps/implement.md`  |
| REQ-0272    | I3 in `steps/implement.md`  |
| REQ-0274    | I4 in `steps/implement.md`  |
| REQ-0276    | I4 in `steps/implement.md`  |
| REQ-0290    | O1 in `steps/document.md`   |
| REQ-0292    | O2 in `steps/document.md`   |
| REQ-0298    | O3 in `steps/document.md`   |
| REQ-0300    | O2 in `steps/document.md`   |
| REQ-0450    | I7 in `steps/implement.md`  |
| REQ-0458    | I9 in `steps/implement.md`  |
| REQ-0460    | I8 in `steps/implement.md`  |
| REQ-0462    | I8 in `steps/implement.md`  |
| REQ-0464    | I8 in `steps/implement.md`  |
| REQ-0466    | I8 in `steps/implement.md`  |
| REQ-2774    | I10 in `steps/implement.md` |
| REQ-3104    | I6 in `steps/implement.md`  |

The prompt check passes on the step files and `meow-method check` reports 0
findings, as the gate below shows. Whether the model follows the rules is
measured by evaluation, which is postponed.

## Left alone

Measuring whether the model follows the rules, which waits for evaluation.
