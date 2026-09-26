---
id: TSK-1540
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1160
closes:
  [
    REQ-0239,
    REQ-0252,
    REQ-0254,
    REQ-0255,
    REQ-0256,
    REQ-0258,
    REQ-0260,
    REQ-0263,
    REQ-0264,
    REQ-0265,
    REQ-0268,
    REQ-0270,
    REQ-0285,
    REQ-0301,
    REQ-0305,
    REQ-0323,
    REQ-2892,
    REQ-2894,
    REQ-2896,
    REQ-2904,
    REQ-3100,
    REQ-3106,
    REQ-3172,
  ]
issue: 224
---

# The epic step carries its obligations

One task, one branch, one pull request, one review.

## What to do

Write each obligation the requirements below place on epic into `steps/epic.md` as a labelled rule, with its reason in the same sentence, naming no requirement identifier, because the file ships to other repositories. Keep the five-tag vocabulary the prompt check holds. Record, under Evidence, a table mapping each requirement this task closes to the label of the rule that carries it, and show the prompt check and `meow-method check` passing.

## Depends on

Nothing. ADR-1160 and SPC-1090 are approved.

## Evidence

Each requirement this task closes is carried by a labelled rule in the step
file named, and every rule names no requirement, because the file ships to
other repositories:

| Requirement | Carried by             |
| ----------- | ---------------------- |
| REQ-0239    | E1 in `steps/epic.md`  |
| REQ-0252    | E2 in `steps/epic.md`  |
| REQ-0254    | E5 in `steps/epic.md`  |
| REQ-0255    | E8 in `steps/epic.md`  |
| REQ-0256    | E6 in `steps/epic.md`  |
| REQ-0258    | E7 in `steps/epic.md`  |
| REQ-0260    | E7 in `steps/epic.md`  |
| REQ-0263    | E2 in `steps/epic.md`  |
| REQ-0264    | E3 in `steps/epic.md`  |
| REQ-0265    | E6 in `steps/epic.md`  |
| REQ-0268    | E9 in `steps/epic.md`  |
| REQ-0270    | E9 in `steps/epic.md`  |
| REQ-0285    | E4 in `steps/epic.md`  |
| REQ-0301    | E10 in `steps/epic.md` |
| REQ-0305    | E10 in `steps/epic.md` |
| REQ-0323    | E10 in `steps/epic.md` |
| REQ-2892    | E12 in `steps/epic.md` |
| REQ-2894    | E12 in `steps/epic.md` |
| REQ-2896    | E13 in `steps/epic.md` |
| REQ-2904    | E11 in `steps/epic.md` |
| REQ-3100    | E3 in `steps/epic.md`  |
| REQ-3106    | E10 in `steps/epic.md` |
| REQ-3172    | E14 in `steps/epic.md` |

The prompt check passes on the step files and `meow-method check` reports 0
findings, as the gate below shows. Whether the model follows the rules is
measured by evaluation, which is postponed.

## Left alone

Measuring whether the model follows the rules, which waits for evaluation.
