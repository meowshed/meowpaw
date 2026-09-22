---
id: TSK-1230
artifact: task
status: draft
revised: 2026-09-22
epic: EPC-1020
closes: [REQ-1130, REQ-1136]
issue:
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

Not yet. The task closes on the check failing on both probes and passing on
the tree, on `mise run all` depending on it, and on the loop's table for the
style and the fragment on both models.

## Left alone

What the style says. TSK-1190 rewrites its content; this task changes its
form and measures that the form costs nothing.
