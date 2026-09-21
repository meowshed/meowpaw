---
id: TSK-1050
artifact: task
status: approved
revised: 2026-09-21
unit: U-0001
epic: EPC-1000
closes: [REQ-0956]
issue: 9
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

**The suite is written and unrun, and there is no delta.** Four cases with
eleven graders sit in `plugins/meow-core/evals/`, weighted towards what this
method produces: an error report, a progress report with nothing to compute
from, an opener that invites a preamble, and a request for brevity over a
report whose one unresolved verb is the thing worth keeping.

Every run is a real model call on the owner's account, in both arms, and the
owner postponed the run rather than spend on it now. The command that produces
the evidence:

```bash
claude plugin eval plugins/meow-core --runs 5 --max-cost-usd 2 --trust-plugin
```

Five runs and not the default three, because RES-0266 records three as a
starting point and no standard, and the one measured evaluation in this corpus
reported single-case variance above 0.9 at three.

What closes this task: that delta, per dimension and weighted, the trial count,
the judge, and the case set at the revision it ran at. A result contradicting
ADR-1000's claim is evidence too, and it is reported and never rerun until it
agrees.

## The judge is not settled

The runner's judge is a small Claude model grading Claude, which REQ-3028 says
is reported as a smoke check and never as the result. `--judge-model` selects
another model through the same credential, so it cannot reach a judge outside
that family.

TypeSafe's Jev is one candidate for the cross-family judge, grading the same
transcripts in a second pass over the runner's JSON: its Score primitive
returns a position on a described scale with per-level probabilities and a
confidence, where the platform's grader returns a pass from two votes of three.
Nothing about it is decided. It needs research and a decision of its own,
because swapping the judge is the kind of change REQ-3028 governs.

## Left alone

No claim is made about the published suite this decision drew on. Its numbers
are cited in ADR-1000 as somebody else's measurement, with its weaknesses, and
this task measures our own shape and not theirs.
