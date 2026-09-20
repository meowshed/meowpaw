---
id: RES-0266
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0005, RES-0070
---

# Measuring the harness

## Summary

The platform can measure what a plugin contributes, which turns _does this
skill earn its cost_ from an argument into a number. Its instrument runs each
case with the plugin and again without it, and reports the difference - so a
case that scores perfectly both ways proves the plugin did nothing. Two of its
defaults are the exact weaknesses this corpus already recorded in the one
worked evaluation it read: three runs per case, and a small fast judge from the
same family as the candidate. Both are settings, so the harness overrides them
and inherits neither.

Research for how the harness measures itself. It does not cover what a skill
costs, which is [RES-0005-skill-format.md](RES-0005-skill-format.md), nor who
may verify what, which is
[RES-0070-who-verifies.md](RES-0070-who-verifies.md).

## The question

Two conclusions in this corpus say measurement belongs in the harness's own
gate, and neither says what is measured, against what, or what counts as a
regression.

Meanwhile the corpus is full of claims that are only arguments: that a shorter
skill body works better, that a description written as when-to-use routes more
reliably, that the ordering of obligations survives compaction. Each is
testable and none has been tested.

## Method

The platform's evaluation documentation was fetched and read on 2026-09-20 for
the case format, the grader types and their costs, the default run count and
threshold, the baseline mechanism, and the judge model.

The monorepo guidance was fetched for its telemetry section, which supplies the
other half - which skills are actually invoked - and was found there rather
than in the skills documentation.

The verification research already in this corpus supplied the bias findings the
defaults have to be read against.

Nothing was measured. No eval suite exists for this harness, so this document
describes an instrument that has not been pointed at anything.

## Findings

### The instrument compares against the absence of the plugin, which is the honest question

A suite lives in the plugin, each case is a realistic prompt plus one or more
graders, and every case runs twice over: once with the plugin loaded and once
without.

The reason is stated plainly and is the finding that matters most:

> A high score on its own doesn't tell you the plugin helped, because Claude
> might do as well without it.

The two arms produce two scores and their difference. And the corollary: _"If a
case scores 1.0 both with and without the plugin, the plugin isn't what made it
pass."_

That is a harder standard than this project has been holding itself to. Most of
the harness's claims are of the form _this instruction makes the model do the
right thing_, and the baseline asks whether the model would have done it
anyway. For a corpus of several hundred obligations, some non-trivial fraction
will turn out to be describing behaviour that was already there.

### Four graders are free and two cost money, which shapes what a suite checks

Of the six grader types, four are computed from the transcript and the
filesystem and cost nothing: a pattern over the reply, whether a tool was
called, the order tools were called in, and whether a file exists. Two call a
judge model and add to the cost: a rubric judged by a model, and a comparison
against the baseline arm.

The free four are enough for most of what this harness needs to know, and this
document states it because the temptation is to write rubrics. _Did it refuse
to guess the verb_ is a pattern. _Did it run the gate before claiming a pass_
is a tool order. _Did it write the artifact_ is a file check. Only _is the
reasoning sound_ needs a judge.

So a suite is mostly free to run, and the expensive part is reserved for the
claims that genuinely require judgement - which is the same division the four
verifiers already draw.

### The default run count is the weakness this corpus already recorded

Each case runs three times by default; a run's score is the fraction of its
graders that passed, and the case's score is the mean across runs. The
documentation is explicit that a single run is noisy and that a change should
be confirmed at the default count before it is trusted.

Three is also exactly the figure the one worked evaluation in this corpus
reported as its own weakness, where three trials left single-case variance
above 0.9.

So the default is a starting point, and no standard. A harness making a claim
about a behaviour change runs more than three, and the number is part of the
claim.

### The default judge is a same-family judge, which the corpus has already argued against

The judge for the two model-graded types is a small fast model by default, with
an option to name a stronger one.

The verification research established that a cross-family judge is stronger
than a same-family one, and that where the same family is used it is recorded
as a limitation of the measurement.

The default here is not merely same-family; it is the same family and a smaller
model. That is acceptable for a cheap smoke check and is not acceptable as
evidence for a claim, and the difference has to be stated in whatever the
harness reports.

### The threshold is a pass mark and the default is perfection

A case passes when its score meets the threshold, which defaults to 1.0 -
every grader passing on every run.

For a deterministic check that is right. For a behavioural claim about a
non-deterministic agent it is a strong requirement, and the honest choice is to
set it deliberately per case, accepting no default. A case that asserts _the
harness always refuses to guess_ should be at 1.0, because a single failure is
the whole defect. A case that asserts _the harness usually chooses the right
skill_ should not, and pretending otherwise produces a suite that is red for
reasons nobody acts on.

### The first thing it finds is a description problem

The documentation names the common first result: a difference near zero with
the _was the skill used_ grader failing, meaning the model is not choosing the
skill on natural phrasing - and the fix is the description, where the body
changes nothing.

That is a direct confirmation of the progressive-disclosure finding that the
description is the only part paid for every turn and exists to answer when to
use the skill. It also means the harness's first measurements will be about
routing, and never about content, which is the right order: a skill that is
never chosen cannot be evaluated for what it says.

### Cost is real, and the shape of it decides how often a suite runs

Every run is a model call on the account. A suite costs roughly its cases times
its runs, doubled for the baseline arm, plus three short judge calls per
model-graded grader per run.

So the suite is not a check that runs on every change. It is closer to the slow
correctness tools in the language research - the mutation testers and the model
checkers - which run on a schedule and on release, and never per commit.

The free graders change that calculus only partly: the agent runs are the cost,
not the grading.

### The other instrument answers what is used

Two measurements already named in this corpus complete the picture, and one was
found in an unexpected place.

The platform's skill report gives token cost per skill against invocation
count, which is what makes _does this skill earn its cost_ answerable.

And the telemetry exporter records a skill-activation event carrying the
skill's name and what triggered the invocation - a command, the model, or
another skill. The monorepo guidance names it as the way to find which skills
go unused and therefore what to consolidate or retire.

That last one is the measurement this harness most needs and had not found: a
catalogue of thirty plugins will contain skills nobody ever loads, and no
amount of reasoning identifies which.

### What the harness should measure about itself

Read against the corpus's own claims, the suite writes itself:

- **Routing.** Is the right skill chosen on natural phrasing - the free grader,
  per skill. - **Refusals.** Does the harness report an unresolved verb and
  guess at nothing; does it decline to approve its own work where that is the
  rule. Patterns and tool checks, no judge needed. - **Order.** Does the gate
  run before the claim; does documentation run before verification. Tool-order
  graders. - **Artifacts.** Does the step produce the file it says it produces,
  with the sections the template requires. File checks. - **Contribution.** For
  every one of those, the difference against no plugin, because an obligation
  the model already honours is a line of instruction being paid for forever.

That last category is the one that will be uncomfortable, and it is the reason
to have the instrument.

## Conclusions

1. Every measurement is made against the absence of the plugin, because a high
   score alone does not show the plugin helped. 2. A case that scores the same
   with and without the harness is a line of instruction to delete, and no
   success. 3. Most graders are free and are preferred: patterns, tool use,
   tool order and file existence cover routing, refusals, ordering and
   artifacts. 4. A judge is used only where the claim genuinely needs
   judgement, which is the same division the four verifiers draw. 5. The
   default of three runs is not enough to support a claim, being the count this
   corpus already recorded as a weakness, and the number used is stated with
   the result. 6. The default judge is a smaller model from the same family, so
   a result that used it is reported as a smoke check, and never as evidence,
   and a claim uses a stronger and preferably cross-family judge. 7. The
   threshold is set per case, and inherited never. A refusal is at perfection
   because one failure is the whole defect; a tendency is not. 8. Routing is
   measured before content, since a skill that is never chosen cannot be
   evaluated for what it says, and the fix for poor routing is the description. 9. The suite runs on a schedule and at release, and never on every change,
   because every run is a real model call and the agent runs dominate the cost. 10. Cost per skill against invocation count is tracked, which is what makes
   a skill's value answerable, where an argument settles nothing. 11. Skill
   activation is recorded through telemetry, because a catalogue will contain
   skills nobody loads and only a count finds them. 12. A regression is a fall
   in the difference against baseline, and never in the absolute score, since
   the absolute score moves when the model changes. 13. A new model release is
   a reason to re-run the suite, because an instruction that compensated for an
   older model's limitation becomes overhead once the limitation is gone.

## Sources

All read 2026-09-20.

- [Test plugins with evals](https://code.claude.com/docs/en/plugin-evals) - the
  suite layout with cases as prompts plus graders; the six grader types with
  four computed from the transcript and files at no cost and two calling a
  judge; three runs per case by default with the run score as the fraction of
  graders passed and the case score as the mean; the threshold defaulting to
  1.0; the no-plugin baseline with its two arms and their difference, and the
  statement that a case scoring 1.0 both ways was not made to pass by the
  plugin; the cost model of cases times runs, doubled for the baseline, plus
  three judge calls per model-graded grader per run; the small fast judge by
  default with the option to name a stronger one; the warning that a single run
  is noisy; and the common first finding of a near-zero difference with the
  skill-used grader failing, fixed in the description. - [Set up Claude Code in
  a monorepo or large
  codebase](https://code.claude.com/docs/en/large-codebases) - the telemetry
  logs exporter and the skill-activation event carrying the skill name and what
  triggered the invocation, named as the way to find which skills go unused. -
  [RES-0005-skill-format.md](RES-0005-skill-format.md) - the per-skill cost and
  invocation report, and the conclusion that measurement belongs in the
  harness's own gate. - [RES-0070-who-verifies.md](RES-0070-who-verifies.md) -
  that a cross-family judge is stronger than a same-family one, that a
  same-family judge is recorded as a limitation, and that an evaluation
  measures something, where a pass settles it. -
  [RES-0038-reporting.md](RES-0038-reporting.md) - the worked evaluation whose
  stated weaknesses were a low trial count leaving variance above 0.9 and a
  judge from the same family as the candidate.
