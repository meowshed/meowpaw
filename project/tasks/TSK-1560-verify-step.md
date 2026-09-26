---
id: TSK-1560
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1160
closes:
  [
    REQ-0241,
    REQ-0275,
    REQ-0277,
    REQ-0278,
    REQ-0279,
    REQ-0280,
    REQ-0281,
    REQ-0282,
    REQ-0283,
    REQ-0284,
    REQ-0286,
    REQ-0288,
    REQ-0291,
    REQ-0293,
    REQ-0295,
    REQ-0296,
    REQ-0297,
    REQ-0299,
    REQ-0307,
    REQ-0317,
    REQ-0319,
    REQ-0325,
    REQ-0327,
    REQ-0329,
    REQ-0542,
  ]
issue: 226
---

# The verify step carries its obligations

One task, one branch, one pull request, one review.

## What to do

Write each obligation the requirements below place on verify into `steps/verify.md` as a labelled rule, with its reason in the same sentence, naming no requirement identifier, because the file ships to other repositories. Keep the five-tag vocabulary the prompt check holds. Record, under Evidence, a table mapping each requirement this task closes to the label of the rule that carries it, and show the prompt check and `meow-method check` passing.

## Depends on

Nothing. ADR-1160 and SPC-1090 are approved.

## Evidence

Each requirement this task closes is carried by a labelled rule in the step
file named, and every rule names no requirement, because the file ships to
other repositories:

| Requirement | Carried by               |
| ----------- | ------------------------ |
| REQ-0241    | V6 in `steps/verify.md`  |
| REQ-0275    | V1 in `steps/verify.md`  |
| REQ-0277    | V1 in `steps/verify.md`  |
| REQ-0278    | V2 in `steps/verify.md`  |
| REQ-0279    | V1 in `steps/verify.md`  |
| REQ-0280    | V3 in `steps/verify.md`  |
| REQ-0281    | V4 in `steps/verify.md`  |
| REQ-0282    | V5 in `steps/verify.md`  |
| REQ-0283    | V4 in `steps/verify.md`  |
| REQ-0284    | V5 in `steps/verify.md`  |
| REQ-0286    | V7 in `steps/verify.md`  |
| REQ-0288    | V8 in `steps/verify.md`  |
| REQ-0291    | V1 in `steps/verify.md`  |
| REQ-0293    | V3 in `steps/verify.md`  |
| REQ-0295    | V5 in `steps/verify.md`  |
| REQ-0296    | V6 in `steps/verify.md`  |
| REQ-0297    | V9 in `steps/verify.md`  |
| REQ-0299    | V5 in `steps/verify.md`  |
| REQ-0307    | V3 in `steps/verify.md`  |
| REQ-0317    | V9 in `steps/verify.md`  |
| REQ-0319    | V2 in `steps/verify.md`  |
| REQ-0325    | V7 in `steps/verify.md`  |
| REQ-0327    | V5 in `steps/verify.md`  |
| REQ-0329    | V10 in `steps/verify.md` |
| REQ-0542    | V2 in `steps/verify.md`  |

The prompt check passes on the step files and `meow-method check` reports 0
findings, as the gate below shows. Whether the model follows the rules is
measured by evaluation, which is postponed.

## Left alone

Measuring whether the model follows the rules, which waits for evaluation.
