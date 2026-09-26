---
id: TSK-1520
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1160
closes:
  [
    REQ-0209,
    REQ-0211,
    REQ-0213,
    REQ-0214,
    REQ-0215,
    REQ-0221,
    REQ-0222,
    REQ-0225,
    REQ-0226,
    REQ-0227,
    REQ-0229,
    REQ-0231,
    REQ-0245,
    REQ-0253,
    REQ-0271,
    REQ-0273,
    REQ-0564,
    REQ-2640,
    REQ-2642,
    REQ-2644,
    REQ-2648,
    REQ-2650,
    REQ-2869,
    REQ-2874,
    REQ-2876,
  ]
issue: 222
---

# The research and requirements steps carry their obligations

One task, one branch, one pull request, one review.

## What to do

Write each obligation the requirements below place on research and requirements into `steps/research.md`, `steps/requirements.md` as a labelled rule, with its reason in the same sentence, naming no requirement identifier, because the file ships to other repositories. Keep the five-tag vocabulary the prompt check holds. Record, under Evidence, a table mapping each requirement this task closes to the label of the rule that carries it, and show the prompt check and `meow-method check` passing.

## Depends on

Nothing. ADR-1160 and SPC-1090 are approved.

## Evidence

Each requirement this task closes is carried by a labelled rule in the step
file named, and every rule names no requirement, because the file ships to
other repositories:

| Requirement | Carried by                    |
| ----------- | ----------------------------- |
| REQ-0209    | R1 in `steps/research.md`     |
| REQ-0211    | R3 in `steps/research.md`     |
| REQ-0213    | Q1 in `steps/requirements.md` |
| REQ-0214    | Q5 in `steps/requirements.md` |
| REQ-0215    | Q2 in `steps/requirements.md` |
| REQ-0221    | R7 in `steps/research.md`     |
| REQ-0222    | R8 in `steps/research.md`     |
| REQ-0225    | R6 in `steps/research.md`     |
| REQ-0226    | R5 in `steps/research.md`     |
| REQ-0227    | R2 in `steps/research.md`     |
| REQ-0229    | R4 in `steps/research.md`     |
| REQ-0231    | Q7 in `steps/requirements.md` |
| REQ-0245    | Q4 in `steps/requirements.md` |
| REQ-0253    | Q3 in `steps/requirements.md` |
| REQ-0271    | Q8 in `steps/requirements.md` |
| REQ-0273    | Q8 in `steps/requirements.md` |
| REQ-0564    | R9 in `steps/research.md`     |
| REQ-2640    | R9 in `steps/research.md`     |
| REQ-2642    | R9 in `steps/research.md`     |
| REQ-2644    | R9 in `steps/research.md`     |
| REQ-2648    | R10 in `steps/research.md`    |
| REQ-2650    | R11 in `steps/research.md`    |
| REQ-2869    | R12 in `steps/research.md`    |
| REQ-2874    | Q9 in `steps/requirements.md` |
| REQ-2876    | Q6 in `steps/requirements.md` |

The prompt check passes on the step files and `meow-method check` reports 0
findings, as the gate below shows. Whether the model follows the rules is
measured by evaluation, which is postponed.

## Left alone

Measuring whether the model follows the rules, which waits for evaluation.
