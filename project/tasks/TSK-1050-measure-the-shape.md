---
id: TSK-1050
artifact: task
status: approved
revised: 2026-09-21
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

Run at `8f9e8dd` with the turn cap raised to 10, on 2026-09-21:

```bash
claude plugin eval plugins/meow-core --runs 5 --trust-plugin -j 4
```

Four cases, five runs per arm, forty agent runs, no run errors, 183 seconds,
$4.25 at list price. The judge is the runner's default, a small Claude model,
which REQ-3028 makes a smoke check and not the result.

| Case                      | WITH | W/OUT | Delta |
| ------------------------- | ---- | ----- | ----- |
| error-report              | 0.70 | 0.45  | +0.25 |
| completeness-over-brevity | 1.00 | 1.00  | 0.00  |
| multi-step-progress       | 1.00 | 1.00  | 0.00  |
| no-preamble-no-recap      | 1.00 | 1.00  | 0.00  |

Mean delta +0.06.

### What the numbers do not support

**Three cases discriminate nothing.** The baseline scores 1.00 on them, so an
unstyled reply already keeps the unresolved verb, already declines to invent a
progress count, and already opens without a preamble. Those cases measure the
model's defaults and say nothing about the shape. That is a defect in the case
set, and the cases are too easy rather than the shape being idle.

**The one case with a delta does not separate its arms.** Per-run scores, with
the style and without it:

```text
with:     0.50  0.50  1.00  0.50  1.00     mean 0.70
without:  0.75  0.75  0.25  0.25  0.25     mean 0.45
```

Two baseline runs beat three styled runs. Five runs per arm cannot tell +0.25
from variance at that spread, which is the weakness RES-0266 recorded before
this suite existed.

**The styled arm is poor in absolute terms.** At 0.70 the style fails
`cause-location-fix` outright in some runs, with three judge votes of FAIL
rather than a split, so the gain is measured against a low ceiling.

### What it means for ADR-1000

The decision leans on a published suite whose two largest gains were multi-step
progress and error reports. This measurement finds a gain on error reports
only, and cannot see one anywhere else.

The reversal condition ADR-1000 names is the shape scoring below the unshaped
baseline on correctness. That did not happen, so the decision stands, on
thinner evidence than it claims. What would settle it is a harder case set and
more runs, and that is the next measurement rather than a rerun of this one.

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
