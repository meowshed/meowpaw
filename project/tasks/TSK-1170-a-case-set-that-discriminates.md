---
id: TSK-1170
artifact: task
status: approved
revised: 2026-09-22
epic: EPC-1010
closes: [REQ-3024, REQ-3030, REQ-3036]
issue: 54
---

# Replace the case set, and build the loop every prompt goes through

One task, one branch, one pull request, one review.

## What to do

Replace the cases under `plugins/meow-core/evals/` that score 1.00 in both
arms. TSK-1050 found three of four in that state, so the current set cannot
see whether a change to the reply shape helped. A case earns its place when it
separates the arms on the text being measured.

Draw the new cases from what this method produces: a progress report with
nothing to compute from, an error report, a gap list somebody asked to shorten,
a summary under pressure to drop a verb. Keep `error-report`, the one case that
moved.

Grade with the cheapest grader the claim allows (REQ-3024): a pattern over the
reply, a tool call, the order of two calls, a file that exists. Spend a judge
only where the question needs reading, such as whether a summary rounded an
unresolved verb into a pass.

Give each case its own threshold (REQ-3030). A refusal sits at perfection,
because one failure is the whole defect, and a tendency does not.

Report a regression as a fall in the difference against the baseline and never
as a fall in the absolute score (REQ-3036). A better model raises both arms, so
the absolute score alone would call an unchanged prompt better.

Run the suite in both arms against the current style, with the run count and
the judge stated as TSK-1050 did.

Build the loop SPC-1020 states as one runner that every prompt in the harness
goes through. Every skill, agent, hook prompt, style and fragment is improved
with it, so building it once keeps each prompt's result comparable with the
others. The runner takes a unit, a baseline and a set of candidates, each
candidate changing one thing. It runs each one on the same cases with the same
run count and the same judge, and it publishes one table: a row per candidate
with its delta against the baseline, its token cost, its run count and whether
it landed. A candidate lands when the delta holds or rises and the token cost
falls. The runner never drops a losing candidate from the table, because a loop
reporting only its winner is an argument dressed as a measurement.

For a prompt that blocks or classifies, such as the gate or the reviewer, the
runner reports the rates on a labelled set in place of a delta, as SPC-1020
describes for measuring a gate.

The owner chose the models. The runner optimises every prompt for Sonnet 5
(`claude-sonnet-5`), the model it runs the candidates on, and judges with
Opus 5.5 (`claude-opus-5-5`), which is stronger than the model it grades. The
gate is the exception: it runs on Haiku in use, so Haiku is the model it is
measured on, and its labelled set needs no judge.

The judge is from the same family as the model it grades, so the runner labels
each judged result a smoke check and never the result (REQ-3028). Choosing a
stronger judge meets half of that requirement, and a judge from another family
would meet the rest. A grader that costs nothing is unaffected, which is one
more reason to prefer one wherever the claim allows (REQ-3024).

The first run of this runner measures the baseline on the models named here
before any candidate, and it counts as the re-run REQ-3038 asks for, because
Opus 5.5 is a new release.

## Depends on

No other task. The instrument is repaired before anything is measured with it,
so this task can start first.

## Evidence

Not yet. The task closes on a run of the runner with the current style as the
baseline and one deliberately worse candidate, which must lose, and on a run of
the new set with the per-case table published, every case separating the
arms, each threshold stated, the run count and the judge named, and the delta
read as the measure of regression.

## Left alone

Every prompt itself. This task measures the current shape as the baseline and
builds the runner, and each task that owns a prompt improves it.
