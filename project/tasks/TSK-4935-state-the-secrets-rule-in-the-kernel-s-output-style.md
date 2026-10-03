---
id: TSK-4935
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2525
closes: [REQ-1424]
issue:
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

Not yet.

## Left alone

`CLAUDE.md`'s `never_touch_secrets`, which states the rule for this
repository and stays, and any program that tries to detect a secret, which
ADR-2460 leaves to review.
