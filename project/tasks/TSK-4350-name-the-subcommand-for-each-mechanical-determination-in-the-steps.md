---
id: TSK-4350
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2330
closes: [REQ-1172, REQ-1178, REQ-1180, REQ-1190]
issue: 942
projected: f756ce7dce42
tracked: 2d7ba9e86530
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

The tests came first, in a commit of their own, where three of the five in
`plugins/meow-flow/tests/test_determinations.py` failed.
`test_every_determination_in_a_step_file_names_a_subcommand` closes criterion 1
(REQ-1172): it reads each paragraph and rule of every step file, fails one
that asks for a count, a coverage, a staleness, a resolution, a readiness or an
allocation and names no `paw` subcommand, and exempts four items that ask for
none, each with its reason in the test. It found two: the implement step's
"where a task of the epic is ready", which now names `paw status`, and the
requirements step's identifier block, which now names `paw new requirement`.
`test_a_step_that_asks_for_a_count_with_no_subcommand_fails` shows the checker
fails a step that says "count the requirements". Two tests close criterion 2:
the method skill's new rules M23 and M24 state what a cited output carries
(REQ-1178) and that a contradiction is reported and not deferred to (REQ-1180).
`test_the_session_start_hook_runs_the_waiting_report` closes criterion 3
(REQ-1190) and held before the change.

No determination was found that needs a subcommand `meow` doesn't have, so
this pull request lists no gap. `mise run all` passed with exit status 0.

## Left alone

The subcommands themselves, which TSK-4330 and TSK-4340 change.
