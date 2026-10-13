---
id: TSK-5065
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2555
closes: [REQ-3052, REQ-3054, REQ-3056]
issue: 990
projected: 519d7c7fc843
tracked: d0a0d520185c
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

`SparseTrees` in `plugins/meow-scm/tests/test_scm.py` closes criterion 1
(REQ-3052) with `test_sparse_paths_list_every_directory_any_agent_reads` and
criterion 2 (REQ-3054) with
`test_settings_that_must_apply_live_in_the_roots_settings_file`, rules T8 and
T9 of the `commit` skill. `ReadDenial` in
`plugins/meow-flow/tests/test_record.py` closes criterion 3 (REQ-3056), rule
I36 of the implement step. Each test reads both the Claude Code and the Pi
copy, and each was seen failing before the rules were added. Whether a run
actually keeps to I36 rests on judgement, because REQ-3056 is verified by an
agent and no program can see what a shell search returned.

Every stage passed in pull request #PR.

## Left alone

The platform's settings precedence, which the rules describe and the harness
doesn't change.
