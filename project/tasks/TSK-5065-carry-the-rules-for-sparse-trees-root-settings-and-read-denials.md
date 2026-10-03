---
id: TSK-5065
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2555
closes: [REQ-3052, REQ-3054, REQ-3056]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Carry the rules for sparse trees, root settings and read denials

The `commit` skill and the implement step carry the three rules SPC-1060
states for parallel agents in working trees: sparse paths list every
directory any agent reads, settings that must apply live in the root's
`.claude/settings.json`, and a read denial is a default and never a boundary.
One task, one branch, one pull request, one review: the tests first, then
the change, its documentation and its marks.

## Acceptance criteria

1. Given `plugins/meow-scm/skills/commit/SKILL.md`, when a test reads it,
   then it carries a rule that sparse paths list every directory any agent
   reads, `.meowpaw/` and `.claude/` included (REQ-3052). Closed by: a test
   under the unit's `tests/` naming REQ-3052, seen failing first.
2. Given the same file, when a test reads it, then it carries a rule that
   settings which must apply in a working tree live in the root's
   `.claude/settings.json` (REQ-3054). Closed by: a test naming REQ-3054.
3. Given `plugins/meow-flow/skills/method/steps/implement.md`, when a test
   reads it, then it carries a rule that no step relies on a read denial to
   keep a file from an agent (REQ-3056). Closed by: a test naming REQ-3056.

## What to do

Add the three rules, each with its reason, to the `commit` skill beside its
rules for one branch in one working tree, and the third to the implement
step's rules, as SPC-1060 states under "Tools that run operations". Hold
both files to SPC-1030 and to each unit's `budget.toml`, and name no tool
other than the ones each file already names.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

The platform's settings precedence, which the rules describe and the harness
doesn't change.
