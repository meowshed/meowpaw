---
id: TSK-4350
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2330
closes: [REQ-1172, REQ-1178, REQ-1180, REQ-1190]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Name the subcommand for each mechanical determination in the method's step files

The method's step files name the `paw` subcommand that computes each count,
coverage, staleness and resolution they need, and the method's rules say how a
subcommand's output is cited and what a step does when it contradicts the
tree, as SPC-1080 states. One task, one branch, one pull request, one review:
the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given `plugins/meow-flow/skills/method/steps/`, when a fixture reads each
   step file, then every place it asks for a count, a coverage, a staleness
   or a resolution names a `paw` subcommand, and a fixture step that asks the
   model to "count the requirements" with no subcommand fails the fixture
   (REQ-1172). Closed by: a fixture naming REQ-1172, seen failing first.
2. Given `plugins/meow-flow/skills/method/SKILL.md`, when a fixture reads it,
   then a rule says a cited output carries the command, its exit status, its
   output and the tree revision, and a rule says a step reports a
   contradiction between a subcommand and the tree and doesn't defer to the
   subcommand (REQ-1178, REQ-1180). Closed by: a fixture naming both.
3. Given `plugins/meow-flow/hooks/hooks.json`, when a fixture reads it, then
   the `SessionStart` hook runs `paw status --waiting` (REQ-1190). Closed by:
   a fixture naming REQ-1190.

## What to do

Read each step file for a count or a comparison the model would make by
reading, and name the subcommand that makes it. Add the two rules to the
method's rules in `SKILL.md`, each with its reason, and hold both files to
SPC-1030 and the unit's `budget.toml`. Where a step needs a determination no
subcommand makes, list it in the pull request as a gap, because ADR-2400
adds no subcommand.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

The subcommands themselves, which TSK-4330 and TSK-4340 change.
