---
id: TSK-1660
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1190
closes:
  [
    REQ-2131,
    REQ-2132,
    REQ-2133,
    REQ-2134,
    REQ-2137,
    REQ-2139,
    REQ-2256,
    REQ-2258,
    REQ-2260,
    REQ-2262,
    REQ-2264,
    REQ-2266,
    REQ-2268,
  ]
issue: 263
---

# The other steps carry their share of the design obligations

The other steps carry their share of the design obligations, as ADR-1190 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given the six step files, when the trace is read, then each requirement this task closes maps to a labelled rule that exists in the file named. Closed by: the trace table and a script finding each label.

## What to do

Append the rules ADR-1190 places on the research, requirements, spec, verify, implement and review steps to each file's rules block, labelled after the existing ones. Record the trace under Evidence.

## Depends on

Nothing. ADR-1190 is approved.

## Evidence

Each requirement this task closes is carried by a labelled rule in the step
file named, and no rule names a requirement:

| Requirement | Carried by                     |
| ----------- | ------------------------------ |
| REQ-2131    | Q10 in `steps/requirements.md` |
| REQ-2132    | Q11 in `steps/requirements.md` |
| REQ-2133    | Q11 in `steps/requirements.md` |
| REQ-2134    | Q11 in `steps/requirements.md` |
| REQ-2137    | R13 in `steps/research.md`     |
| REQ-2139    | R14 in `steps/research.md`     |
| REQ-2256    | S12 in `steps/spec.md`         |
| REQ-2258    | S13 in `steps/spec.md`         |
| REQ-2260    | V11 in `steps/verify.md`       |
| REQ-2262    | V11 in `steps/verify.md`       |
| REQ-2264    | V11 in `steps/verify.md`       |
| REQ-2266    | I11 in `steps/implement.md`    |
| REQ-2268    | W10 in `steps/review.md`       |

The prompt check and `meow-method check` pass, as the gate shows, and a
script found every traced label in its step file. Whether the model follows
the rules is measured by evaluation, which is postponed.

## Left alone

Measuring whether the model follows the rules, which waits for evaluation.
