---
id: TSK-5040
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2570
closes: [REQ-1670]
issue:
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

Not yet.

## Left alone

The defect and decision templates, which already carry what the record needs.
