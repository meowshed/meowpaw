---
id: TSK-1050
artifact: task
status: draft
revised: 2026-09-21
unit: U-0001
epic: EPC-1000
closes: [REQ-0956]
issue:
---

# Measure the shape against the shape it replaces

One task, one branch, one pull request, one review.

## What to do

Build the harness's first evaluation and run it. A change to the reply shape is
measured against the shape it replaces, on a stated case set, with a rubric and
a judge that does not know which condition it is grading (REQ-0956).

What it consists of:

- A case set, stated in the repository, weighted towards what this method
  actually produces: multi-step progress reports and error reports.
- A rubric scoring correctness, actionability, safety and concision, with the
  weights written down before the run.
- A judge grading blind, on labels shuffled per case.
- Several trials, with the count reported (REQ-3026).
- The same work run without the harness as the baseline (REQ-3022), and a
  same-family judge reported as a smoke check and not as the result (REQ-3028).

Publish the delta, per dimension and weighted, including the dimensions that
lost. Concision losing is not a failure: REQ-0950 already subordinates it.

## Depends on

TSK-1020, because the shape under measurement is the one the style carries.

## Evidence

The published delta, the trial count, the judge, and the case set at the
revision it ran at. A result that contradicts ADR-1000's claim is evidence too,
and it is reported and not rerun until it agrees.

## Left alone

No claim is made about the published suite this decision drew on. Its numbers
are cited in ADR-1000 as somebody else's measurement, with its weaknesses, and
this task measures our own shape and not theirs.
