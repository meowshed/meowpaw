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

Run on 2026-09-22 with `tools/loop.py`, which this task adds:

```bash
python3 tools/loop.py plugins/meow-core --candidates <dir holding one candidate>
```

Model `claude-sonnet-5`, judge `claude-opus-5-5`, five runs per arm, no run
errors, $7.77. Every judged score is a smoke check, because the judge is from
the model's own family (REQ-3028).

| Candidate | Change                                               | Delta | 2SE  | Tokens | Verdict                             |
| --------- | ---------------------------------------------------- | ----- | ---- | ------ | ----------------------------------- |
| baseline  | the style as it stands                               | +0.03 | 0.12 | 1452   | baseline                            |
| hollow    | replace every rule with the habits the shape forbids | -0.31 | 0.10 | 127    | loses: delta fell by more than 0.16 |

The deliberately worse candidate costs a tenth of the tokens and still loses,
so the runner refuses a saving that costs the score. The token counts come from
the model's own tokenizer: the difference in input tokens between a call with
the text appended and one without it.

That run carried five cases. `no-recap` scored 1.00 in both arms and was
removed afterwards, so the set that ships is the four below, taken from the
same run. Their mean delta is +0.04.

| Case                     | With | Without | Delta | Threshold | Meets it |
| ------------------------ | ---- | ------- | ----- | --------- | -------- |
| `error-report`           | 0.85 | 0.80    | +0.05 | 0.75      | yes      |
| `gap-list-kept`          | 0.60 | 1.00    | -0.40 | 1.0       | no       |
| `no-preamble-no-recap`   | 0.80 | 0.50    | +0.30 | 0.8       | yes      |
| `one-line-keeps-the-gap` | 1.00 | 0.80    | +0.20 | 1.0       | yes      |

Every case separates the arms. A screen at three runs per arm removed six
candidates that scored the same in both: `completeness-over-brevity`,
`multi-step-progress`, `opens-with-the-answer`, `offer-at-the-end`,
`no-bold-paragraph-openers` and `hedge-kept`. Sonnet 5 already does each of
those things without the style.

`error-report` was kept by name and rewritten. Its old prompt quoted a
compiler's type error, and the styled arm failed it on every run by misreading
which type was expected, so it measured how the model reads that language and
not the reply shape. The old prompt also put a language name and a build tool
into the kernel, which the constitution forbids.

`gap-list-kept` is a regression the current style causes. In two runs of five
the styled reply answered "2 and 4" and folded the other three questions into
one clause, where the unstyled reply kept all five. Leading with the action
overrides keeping every question, and TSK-1190 owns the fix.

The baseline gains +0.04 on Sonnet 5, against +0.06 on the old set with the
runner's default model. The style as it stands barely separates from the model
it runs on, which is what TSK-1190 starts from.

## Left alone

Every prompt itself. This task measures the current shape as the baseline and
builds the runner, and each task that owns a prompt improves it.
