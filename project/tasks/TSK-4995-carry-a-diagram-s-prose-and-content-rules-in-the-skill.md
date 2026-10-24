---
id: TSK-4995
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2540
closes: [REQ-2300, REQ-2302]
issue: 979
projected: 276f84bb35a6
tracked: 5fe4a2eb0f87
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Carry a diagram's prose and content rules in the skill

The Markdown skill and `reviewing.md` state that everything a diagram asserts
is also stated in the prose beside it, and that a diagram carries no
obligation and no reason, as SPC-1195 states under "Diagrams". One task, one branch, one pull request, one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given `plugins/meow-markdown/skills/markdown/reviewing.md`, when a fixture test reads it, then it carries both rules, each with its reason (REQ-2300, REQ-2302). Closed by: a fixture under `plugins/meow-markdown/tests/` naming both requirements, seen failing first.
2. Given the changed skill, when `meow-author check` and `meow-author cost` run, then both pass and the unit stays within its `budget.toml`. Closed by: the `lint` verb's `prompts` and `budget` tasks.

## What to do

Edit `reviewing.md`, and the skill's body where it names diagram blocks, to
the form SPC-1030 states. Whether a reviewer applies the rules on a real
document rests on judgement, because no fixture reads what a diagram claims.

## Depends on

Nothing.

## Evidence

Criterion 1 is closed by `test_tsk_4995_criterion_1_reviewing_carries_both_diagram_rules_with_reasons` in `plugins/meow-markdown/tests/test_markdown.py` (REQ-2300, REQ-2302), seen failing first. Criterion 2 is closed by the `prompts` and `budget` tasks of the `lint` verb.

Whether a reviewer applies the two rules to a real document rests on judgement, because no fixture reads what a diagram claims.

Every stage passed in pull request #PR.

## Left alone

The writing standard in `meow-prose`, which already says a fact belongs in the
prose, and needs no diagram rule of its own.
