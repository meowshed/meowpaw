---
id: ADR-1500
artifact: adr
status: approved
revised: 2026-09-27
addresses:
  [REQ-0153, REQ-0159, REQ-0160, REQ-1759, REQ-3022, REQ-3026, REQ-3028]
supersedes: []
---

# 1500. The evaluation loop reports what a measurement rests on, and refuses what it can't hold

## Decision

`tools/loop.py` stays the one way the harness measures a change to its own
material, through the platform's `claude plugin eval` (REQ-1759). This
decision settles what it reports with every result and what it refuses to
run.

Every mode runs both arms, the unit and the same work without it
(REQ-3022). Classifier mode, which today runs the unit alone, gains the arm
without it and reports, for defect cases and clean cases each, the pass rate
with the unit, without it, and the delta. Each case gets one of three labels
from its delta and twice its standard error, against a margin of 0.10 the code
states before any run. Where the whole interval lies within the margin of
zero, the case is reported as `delete: scores the same without the unit`,
because it measures nothing the unit does. Where the interval clears zero, the
case separates. Where it does neither, the case is reported as
`undetermined: run more`, because too few runs to find a difference aren't a
finding that none exists.

Every rate and delta carries twice its standard error, and every case its run
count (REQ-0160, REQ-3026). Classifier mode, which reports rates alone today,
gains the error of each rate. The runs default to 5, a cost I chose above the
platform's 3, and the error printed beside each result shows whether 5 was
enough for that case. The header names the count, and at 3 or fewer it says
the result supports no claim, because REQ-3026 rules the platform's 3 out.

The header names the judge's model and its family, taken from the model's
identifier, and where the judge's family is the candidate's it says every
judged score, a candidate's verdict included, is a smoke check and no evidence
for a claim (REQ-0160, REQ-3028). A verdict decides whether a text change
lands in this repository, which a smoke check can inform, and it is never
cited as a claim about the harness. Where the judge is the candidate's own
model, the header says that too. Where the judge is from another family, the
header says the result is not a smoke check by family, and that it is still no
claim, because which judge counts as stronger than a candidate, which REQ-3028
also asks for, the loop doesn't settle. The loop computes the family instead
of printing a fixed sentence.

What counts is stated before a run in two places (REQ-0159). The code states
the delta that counts: a case counts only where its delta clears twice its
standard error, and a candidate lands only where its delta falls by no more
than twice the combined standard error. The unit's `evals/thresholds.toml`
states, per case, the minimum score with the unit, which the case must also
reach. The loop refuses to run while that file differs from the last commit,
and the report's header names that commit and the time of the run, so a
reader can check the threshold was committed before the result it judges. A
case with no threshold runs and gets no verdict, reported as
`no threshold set before the run`, because a threshold added after it would be
chosen to fit.

The loop refuses a case with a grader of `type: baseline`. RES-0266 describes
it as a model-judged comparison against the baseline arm, and the runner's
reference, read 2026-09-27, gives it only a baseline file and criteria and says
nothing of what its judge sees or in what order, so the harness can't shuffle
the order of what it compares (REQ-0153). Every other grader type the loop
accepts judges one run's output alone, and a comparison the loop makes,
candidate against baseline, compares scores and never shows a judge two outputs
at once. A comparison added later that shows a judge two outputs shuffles their
order per case.

After this decision every result the loop prints says how many runs it rests
on, how much it varies, who judged it and whether the unit made a difference
or can't yet be told, and names the committed thresholds it judged against.
What still doesn't work: the loop's judge, Opus 5.5, is from the candidates'
own family, so the loop reports smoke checks and no claim.

## Why

RES-0266 found that a high score alone doesn't show the harness helped, and
that a case must be run without the harness to show it did. It recorded that
three runs per case, the platform's default, left a single case's variance
above 0.9 in an evaluation it read, and it found that a judge from the
candidate's family makes a result a smoke check.

RES-0070 found that an evaluation is a measurement and not a pass, so using
one as a gate means stating the delta that counts before running it and
recording the variance and the judge's family beside the result. It found that
position bias in a comparison is large, differs by judge and is not noise, so
order is shuffled per case.

A threshold file that has to match the last commit, named in the report with
the run's time, is the smallest mechanism that makes "before" checkable: the
loop runs by hand and the history records no run, so the report has to carry
the link between the two.

The strongest objection: refusing to run with an uncommitted threshold file
slows the first iteration on a new case, where the author sets a threshold and
wants to try it at once. It does, by one commit, and a threshold tried and
then edited to fit the result is the failure REQ-0159 exists to stop.

## Alternatives

| Option                                         | Better at                                  | Why it lost                                                                                                                 |
| ---------------------------------------------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| Leave the loop as it is                        | No change                                  | Classifier mode has no arm without the unit and no variance, and nothing shows a threshold was set before its result        |
| Record the threshold file's hash in the report | No commit needed before a run              | The hash shows which thresholds a run read, not that they existed before it; a threshold edited after a look still matches  |
| Allow `baseline` graders and trust the runner  | Cases can compare against the baseline arm | The runner documents nothing about the order its judge sees, so the harness would report a comparison it can't show is fair |
| Keep classifier mode on the unit alone         | Half the cost of a run                     | A case that passes without the unit shows nothing about the unit, which RES-0266 names as the failure                       |

## What it costs

Classifier runs double in cost, paid by whoever runs the loop by hand, because
the arm without the unit runs every case again, and the default of 5 runs costs
about 5/3 of the platform's 3 per arm, paid by the same person. A case's author
has to commit its threshold before its case can reach a verdict. A unit that
wants a judged comparison against the baseline arm can't have one until the
runner documents its order or the harness shuffles it.

## What would reverse it

I would allow `baseline` graders if the runner documented that it randomises
the order its judge sees per case. I would drop the committed-threshold rule
if, over the next ten cases added to this repository, it cost their authors
more than one extra commit each, counted in the history.

## Consequences

- `tools/loop.py` runs both arms in every mode, reports variance and runs per
  case, names the judge's family and the threshold commit, flags cases to
  delete, gives no verdict to a case with no threshold, and refuses an
  uncommitted threshold file or a `baseline` grader.
- SPC-1020 states the loop's report and refusals, and drops its sentence
  saying nothing implements it.

## How I will know it was realised

1. Unit tests of `tools/loop.py`, run by the `test` verb with no model call,
   show a case whose interval lies within the margin of zero flagged for
   deletion, a case whose interval is wider than the margin reported as
   undetermined, a rate reported with its error, the judge's family computed
   from its identifier and the header's wording for each family, a run of 3 or
   fewer said to support no claim, a candidate landing only within twice the
   combined error, a case falling short of its threshold given no pass, a case
   with no threshold given no verdict, the threshold commit named in the
   header, and each refusal: a threshold file differing from the last commit,
   and a `baseline` grader.
2. A loop run by hand on `meow-flow`'s cases prints both arms, the error of
   each rate, the run count and the judge's family.
3. Every requirement ADR-1500 addresses lands in exactly one closed task.

## What this does not settle

- A cross-family judge, which the loop doesn't use.
- Which judge counts as stronger than a candidate, which REQ-3028 asks for.
- Evaluating the other units' cases in both arms, which the next run of each
  does by itself.
