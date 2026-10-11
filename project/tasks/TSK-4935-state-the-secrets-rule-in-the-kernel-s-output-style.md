---
id: TSK-4935
artifact: task
status: done
revised: 2026-10-11
epic: EPC-2525
closes: [REQ-1424]
issue: 970
projected: 4531a4d6cf4c
tracked: f1990267963a
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# State the secrets rule in the kernel's output style

`meow-core`'s output style gains one rule: never read, print or send a
repository's secret material, and never put it in an artifact, with its
reason, as SPC-1080 states under "What the harness writes and reads". One
task, one branch, one pull request, one review: the tests first, then the
change, its documentation and its marks.

## Acceptance criteria

1. Given `plugins/meow-core/output-styles/meow.md`, when a test reads it, then
   it carries a rule stating the four prohibitions REQ-1424 names (REQ-1424).
   Closed by: a test under `tools/` naming REQ-1424, seen failing first.
2. Given the changed style, when `mise run budget` runs, then the style stays
   within `permanent_characters` in `plugins/meow-core/budget.toml`, 4,200,
   from 3,945 today. Closed by: the gate's `budget` task.
3. Given the changed style, when `mise run style` and `tools/check_kernel.py`
   run, then both pass, because the rule names no unit outside the kernel.
   Closed by: the gate's `lint` and `test` verbs.
4. Given the style's measured cases under `plugins/meow-core/evals/`, when
   they are run again by hand on Sonnet 5 and Opus 5.5, then each meets its
   threshold in `thresholds.toml`. Closed by: the hand run's output in the
   pull request, which rests on judgement where a case is judged.

## What to do

Write the rule in the style's rule form, held to SPC-1030 and SPC-1000, and
keep it within the budget: if it doesn't fit, raise the budget in the same
change with the reason, as SPC-1030 states. Update the threat model row in
SPC-1080 only if the wording of the control changes.

## Depends on

Nothing.

## Evidence

The tests came first, in a commit of their own, where
`test_the_rule_states_the_four_prohibitions` in `tools/test_secrets_rule.py` failed. It closes
criterion 1 (REQ-1424): the rule is R11, with `read`, `print`, `transmit` and `artifact` and its
reason. Criterion 2 is closed by the budget: the style grew from 3,945 to 4,212 characters, over
the 4,200 it was held to, so the budget is 4,500 with the reason in `budget.toml` and the
manifest names the new ceiling, as the budget's comment asks of a new rule. `mise run style` and
`tools/check_kernel.py` pass, closing criterion 3. Criterion 4 rests on judgement: the measured cases would each be
a model call on Sonnet 5 and Opus 5.5, which run by hand and cost money, and on 2026-10-11 the
owner closed the task on review without re-running them, so the rule rests on the instruction and
on review, as the epic's Not covered states. `mise run all` passed with exit status 0.

## Left alone

`CLAUDE.md`'s `never_touch_secrets`, which states the rule for this
repository and stays, and any program that tries to detect a secret, which
ADR-2460 leaves to review.
