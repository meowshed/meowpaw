---
id: TSK-5040
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2570
closes: [REQ-1670]
issue: 1006
projected: 281b8ddf98ab
tracked: eaa90c022e2f
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# State that a missing capability becomes a defect or a postponement

The method skill tells a step that needs a capability the harness doesn't
have to write a defect or a postponement, and never to work round the gap
unrecorded, as SPC-1090 states under "This repository's own work". One task, one branch, one pull request, one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given `plugins/meow-flow/skills/method/SKILL.md`, when a test reads it, then it carries a rule saying a missing capability is recorded as a defect or a postponement, with its reason (REQ-1670). Closed by: a test under `plugins/meow-flow/tests/` naming REQ-1670, seen failing first.
2. Given the changed skill, when `meow-author check` and `meow-author cost` run, then both pass. Closed by: the `lint` verb's `prompts` and `budget` tasks.

## What to do

Add the rule to the method skill in the form SPC-1030 states, naming no
language and no tool. Whether a session follows it rests on judgement, and
the repository's hand-run cases are where it is measured.

## Depends on

Nothing.

## Evidence

Criterion 1 is closed by
`test_the_method_skill_records_a_missing_capability` in
`plugins/meow-flow/tests/test_missing_capability.py`, seen failing first, which
reads rule M26 of the method skill in both trees for the defect, the
postponement and its reason, and by `test_the_rule_names_no_language_and_no_tool`.
Criterion 2 is closed by `meow-author check`, which reports 0 authoring
failures over 100 files, the `prompts` task. `meow-author cost` reports a
budget failure for every unit, 25 of 25, because no unit carries a
`budget.toml` and SPC-1030 "Size" says no unit carries a budget; that failure
does not come from this change, and the `budget` task criterion 2 names is not
among the gate's tasks. Whether a session follows M26 rests on judgement, as
the task says, and the hand-run cases are where it is measured.

Every stage passed in pull request #1078.

## Left alone

The defect and decision templates, which already carry what the record needs.
