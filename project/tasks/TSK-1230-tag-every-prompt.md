---
id: TSK-1230
artifact: task
status: approved
revised: 2026-09-22
epic: EPC-1020
closes: [REQ-1130, REQ-1136]
issue: 66
---

# Tag every shipped prompt, and measure on both models

One task, one branch, one pull request, one review.

## What to do

Write a check that reads every prompt the harness ships and fails, naming the
file and the line, on a Markdown heading outside a fenced block and on a tag
outside the vocabulary SPC-1010 states (REQ-1130). See it fail first on two
probe prompts, one with a heading and one with an unknown tag (REQ-2072), and
run it in the gate.

Convert the `meow-core` style and fragment to the vocabulary. Each rule states
what to do, and a rule teaching a judgement shows the failing and the
corrected form in `<before>` and `<after>` (REQ-1136).

Extend `tools/loop.py` to run each candidate on Sonnet 5 and on Opus 5.5,
judged by Opus 5.5, and to land a candidate only when it holds on both. Then
measure the tagged style and fragment against the Markdown versions they
replace.

## Depends on

No other task. The `meow-core` prompts exist, and the prompts `meow-prose`
ships are written to the vocabulary when their own tasks write them.

## Evidence

Closed by #79, in the form ADR-1030 and ADR-1040 state.

`tools/check_prompts.py` reads every shipped prompt and runs in the gate as
`mise run prompts`. It failed first on probes with a heading, with a tag outside
the vocabulary, and with a `<rule>` nested inside `<rules>` (REQ-2072), and it
passes on the tree: 24 shipped prompts, 0 failures. `tools/check_style.py`
reads a rule as a list item led by an identifier, and failed on a probe rule
stating no condition under which it yields.

The `meow-core` style is converted, each rule stated as what to do (REQ-1136),
and its fragment is folded into it as ADR-1040 decides: a dispatching prompt
includes the style's rules block. `tools/check_subagent_shape.py` failed on a
probe that dispatches without naming the style, and passes on the tree.

`tools/loop.py` measures each candidate on Sonnet 5 and Opus 5.5, judged by
Opus 5.5, and lands one only when it lands on both. The converted style against
the one it replaces, five runs per arm, $13.41:

| Model    | Current style, delta (2SE) | Converted style, delta (2SE) | Tokens     | Verdict |
| -------- | -------------------------- | ---------------------------- | ---------- | ------- |
| Sonnet 5 | +0.09 (0.13)               | +0.00 (0.14)                 | 1452, 1279 | lands   |
| Opus 5.5 | +0.02 (0.03)               | +0.00 (0.00)                 | 1452, 1279 | lands   |

The converted style holds within the noise on both models and costs 173 fewer
tokens a turn. Its point estimates are lower, and the noise is as large as the
gap: the unstyled arm of `no-preamble-no-recap` scored 0.50 in one run of the
suite and 0.80 in the other. On Opus 5.5 three of the four cases score the
same in both arms, so they show nothing about the style on that model. Every
judged score is a smoke check (REQ-3028).

The fragment is not measured, because no case dispatches a subordinate agent.
TSK-1190 builds those cases.

## Left alone

What the style says. TSK-1190 rewrites its content; this task changes its
form and measures that the form costs nothing.
