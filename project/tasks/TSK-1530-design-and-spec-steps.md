---
id: TSK-1530
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1160
closes:
  [
    REQ-0230,
    REQ-0232,
    REQ-0233,
    REQ-0235,
    REQ-0236,
    REQ-0242,
    REQ-0243,
    REQ-0244,
    REQ-0248,
    REQ-0249,
    REQ-0250,
    REQ-0251,
    REQ-0331,
    REQ-0333,
    REQ-0335,
    REQ-0337,
    REQ-0339,
    REQ-0341,
    REQ-0566,
    REQ-0613,
    REQ-2638,
    REQ-2652,
    REQ-2694,
    REQ-2858,
    REQ-2859,
    REQ-2860,
    REQ-2861,
    REQ-2862,
    REQ-2888,
    REQ-2890,
  ]
issue: 223
---

# The design and spec steps carry their obligations

One task, one branch, one pull request, one review.

## What to do

Write each obligation the requirements below place on design and spec into `steps/design.md`, `steps/spec.md` as a labelled rule, with its reason in the same sentence, naming no requirement identifier, because the file ships to other repositories. Keep the five-tag vocabulary the prompt check holds. Record, under Evidence, a table mapping each requirement this task closes to the label of the rule that carries it, and show the prompt check and `meow-method check` passing.

## Depends on

Nothing. ADR-1160 and SPC-1090 are approved.

## Evidence

Each requirement this task closes is carried by a labelled rule in the step
file named, and every rule names no requirement, because the file ships to
other repositories:

| Requirement | Carried by               |
| ----------- | ------------------------ |
| REQ-0230    | D1 in `steps/design.md`  |
| REQ-0232    | D1 in `steps/design.md`  |
| REQ-0233    | D1 in `steps/design.md`  |
| REQ-0235    | D1 in `steps/design.md`  |
| REQ-0236    | D4 in `steps/design.md`  |
| REQ-0242    | S1 in `steps/spec.md`    |
| REQ-0243    | S11 in `steps/spec.md`   |
| REQ-0244    | S1 in `steps/spec.md`    |
| REQ-0248    | S2 in `steps/spec.md`    |
| REQ-0249    | D8 in `steps/design.md`  |
| REQ-0250    | S3 in `steps/spec.md`    |
| REQ-0251    | D9 in `steps/design.md`  |
| REQ-0331    | S5 in `steps/spec.md`    |
| REQ-0333    | S5 in `steps/spec.md`    |
| REQ-0335    | S4 in `steps/spec.md`    |
| REQ-0337    | S4 in `steps/spec.md`    |
| REQ-0339    | S3 in `steps/spec.md`    |
| REQ-0341    | S7 in `steps/spec.md`    |
| REQ-0566    | D6 in `steps/design.md`  |
| REQ-0613    | S10 in `steps/spec.md`   |
| REQ-2638    | D10 in `steps/design.md` |
| REQ-2652    | D7 in `steps/design.md`  |
| REQ-2694    | D2 in `steps/design.md`  |
| REQ-2858    | S8 in `steps/spec.md`    |
| REQ-2859    | S8 in `steps/spec.md`    |
| REQ-2860    | S6 in `steps/spec.md`    |
| REQ-2861    | S6 in `steps/spec.md`    |
| REQ-2862    | S9 in `steps/spec.md`    |
| REQ-2888    | D3 in `steps/design.md`  |
| REQ-2890    | D5 in `steps/design.md`  |

The prompt check passes on the step files and `meow-method check` reports 0
findings, as the gate below shows. Whether the model follows the rules is
measured by evaluation, which is postponed.

## Left alone

Measuring whether the model follows the rules, which waits for evaluation.
