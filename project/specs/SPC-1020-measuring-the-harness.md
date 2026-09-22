---
id: SPC-1020
artifact: spec
status: live
revised: 2026-09-22
checked-at:
states:
  [
    REQ-0956,
    REQ-3022,
    REQ-3024,
    REQ-3026,
    REQ-3028,
    REQ-3030,
    REQ-3032,
    REQ-3034,
    REQ-3036,
    REQ-3038,
  ]
---

# Measuring the harness

## Scope

Measuring a change to what the harness says is what this covers: the case set,
the two arms, the judge, the thresholds, what counts as a regression, and the
loop by which a prompt is optimised.

It leaves what the prompts say to SPC-1000 and SPC-1010. It leaves the size
budget a unit carries to SPC-1010, which states it alongside the standard the
unit ships.

Nothing implements this yet. ADR-1010 authorises it and EPC-1010 realises it,
and `checked-at` stays empty until that epic closes.

## Boundary

| Surface                                | What it is                                                     |
| -------------------------------------- | -------------------------------------------------------------- |
| `plugins/<unit>/evals/<case>/`         | One case: the prompt a person might type, and its graders      |
| The platform's eval runner             | Runs each case in both arms and scores it                      |
| `plugins/<unit>/evals/results/`        | What a run wrote; no repository commits it                     |
| `plugins/<unit>/evals/thresholds.toml` | What the styled arm must score on each case                    |
| `tools/loop.py`                        | Runs the baseline and every candidate, and publishes one table |
| The published delta                    | Per case and weighted, with the run count and the judge named  |

## Behaviour

### Two arms, always

Every measurement runs the same work with the harness and without it, and the
difference between the two is the result (REQ-3022). A case scoring the same in
both arms measures the model and says nothing about the harness.

### When a case earns its place

A case belongs in the set when it separates the arms on the text being
measured. A case set where the baseline already scores 1.00 cannot see a
change, which the first measurement of SPC-1000 found on three cases of four.

Cases come from what this method produces: a progress report with nothing to
compute from, an error report, a gap list somebody asked to shorten, a summary
under pressure to drop a verb.

Each case carries its own threshold (REQ-3030). A threshold inherited from the
suite says the same thing about a case nobody tuned and a case somebody did.

### Routing before content

The measurement asks whether a unit is chosen before it asks what the unit says
(REQ-3032), because a unit nobody loads has no effect to measure. For a skill
that means its description, and the question is whether the skill fires on
natural phrasing.

### Graders, and when to spend a judge

The measurement prefers a grader that costs nothing: a pattern over the reply,
a tool call, the order of two calls, a file that exists. It spends a judge last
(REQ-3024), and only where the question needs reading: whether a summary
rounded an unresolved verb into a pass, whether a report invented a state.

Where the judge comes from the same family as the text under test, the
measurement reports it as a smoke check and never as the result (REQ-3028).

### What the run states

A measurement states how many runs it used, and nobody assumes the platform's
default of three is enough (REQ-3026). The one measured evaluation this corpus
cites reported single-case variance above 0.9 at three trials.

It states the judge, the case set, the revision it ran at, and the cost in
tokens the unit under test loads on every turn.

### What a regression is

A regression is a fall in the difference against the baseline, and never a fall
in the absolute score (REQ-3036). A model that improved raises both arms, and
reading the absolute score alone would call an unchanged prompt better.

### The loop

A change to a prompt is measured against the prompt it replaces (REQ-0956).
Every prompt goes through one runner, which measures on Sonnet 5 and judges
with Opus 5.5, so a result for one prompt reads the same as a result for
another. Opus 5.5 may also propose and refine the candidates: proposing is not
judging, so the family rule in REQ-3028 does not reach it. The current text is
the baseline. Each candidate changes one thing, so the delta
can be attributed. Each candidate is measured on the same cases, with the same
run count and the same judge.

A candidate lands when the difference holds or rises and the token cost falls.
A candidate scoring better at a higher cost is a judgement, reported with both
numbers.

Every candidate's delta is published, including the ones that lost. Where no
candidate lands, the baseline stays and the loop reports that it found nothing
better, which is a result and not a failure.

### Measuring a gate

A prompt that blocks is measured as a classifier and not as a delta. Its case
set is labelled: texts carrying a named defect, which it must block, and clean
texts, which it must pass. The result is how often it blocks each kind.

A false block costs more than a miss. A gate that stops a good text teaches an
author to work around it, and then it stops nothing; a gate that misses a
defect leaves the deep reviewer and the reader where they already were.

The same numbers decide the model. Haiku is named because these criteria sit
inside what a small model settles, and a rise in false blocks is the evidence
that they do not.

### When the suite runs

The suite runs on a schedule and at release (REQ-3034), which keeps it
affordable, and a model release is its own reason to run it again (REQ-3038).

## Failure paths

| Condition                                     | What happens                                                                                    |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| A case scores the same in both arms           | The case is reported as unable to discriminate, and it is not counted as a pass                 |
| The run hits a usage limit                    | The error is reported as a run error, and never as a plugin regression                          |
| A cost ceiling aborts the run                 | The partial result is reported as partial, and arms graded under different rules print no delta |
| The judge is from the candidate's family      | The result is reported as a smoke check                                                         |
| A candidate improves the score and costs more | Both numbers are published and somebody decides                                                 |
| A measurement contradicts the decision        | It is reported as it stands, and it is not rerun until it agrees                                |
