---
id: TSK-4370
artifact: task
status: done
revised: 2026-10-03
realises: ADR-2420
closes: [REQ-2608, REQ-2610, REQ-2612, REQ-2614, REQ-2616, REQ-2618, REQ-2620]
issue: 899
projected: e0b66700b920
tracked: cceae49f2bc3
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Bound a tool that runs source control operations, in the `commit` skill

The `commit` skill that `meow-scm` ships lists the composite commands it never
runs, uses no generated message, rebases nothing on its own where commits are
signed, cites no model-written summary as evidence, and removes a working
tree only in the foreground, sharing only ignored output, as SPC-1060 states
under "Tools that run operations". One task, one branch, one pull request,
one review: the tests first, then the change, its documentation and its
marks.

## Acceptance criteria

1. Given `plugins/meow-scm/skills/commit/`, when a fixture reads it, then it
   lists the composite commands it never runs, `wt merge` among them, each
   with its reason (REQ-2610). Closed by: a fixture naming REQ-2610, seen
   failing first.
2. Given the skill's steps, when a fixture reads them, then a message is used
   only after `meow-scm check-message` passes, and the skill says a message a
   tool generated is never used (REQ-2612). Closed by: a fixture naming
   REQ-2612.
3. Given the skill, when a fixture reads it, then it says a tool with no
   documented machine-readable output runs operations only and the state is
   read from git (REQ-2608), a rebase after signing is signed again and no
   workflow rebases on its own where signatures are required (REQ-2614), and
   a model-written summary is never cited as evidence (REQ-2616). Closed by:
   a fixture naming the three.
4. Given the skill, when a fixture reads it, then it says a working tree is
   removed only in the foreground, when the person or the step that made it
   asks, and that working trees share only ignored build output (REQ-2618,
   REQ-2620). Closed by: a fixture naming both.

## What to do

Add the rules to `plugins/meow-scm/skills/commit/SKILL.md`, each with its
reason, beside the branch rules it already carries. Hold the skill to
SPC-1030 and to `plugins/meow-scm/budget.toml`, moving material to a
supporting file the core names if the budget would otherwise pass. Update
`plugins/meow-scm/README.md` where it summarises the skill.

ADR-2420 names "the git unit's skill" as the place for criterion 4, and
`meow-git` ships no skill, so I put the rule in the `commit` skill, which
SPC-1060 already names as the carrier of the git discipline.

## Depends on

Nothing.

## Evidence

The tests came first, in a commit of their own, where all six in
`plugins/meow-scm/tests/test_scm.py` class `ToolOperations` failed.
`test_it_lists_the_composite_commands_it_never_runs_with_a_reason` closes
criterion 1 (REQ-2610), and
`test_a_message_a_tool_generated_is_never_used` closes criterion 2 (REQ-2612).
`test_a_tool_with_no_machine_readable_output_runs_operations_only`,
`test_a_rebase_after_signing_is_signed_again_and_never_automatic` and
`test_a_model_written_summary_is_never_evidence` close criterion 3 (REQ-2608,
REQ-2614, REQ-2616), and `test_a_working_tree_is_removed_only_in_the_foreground`
closes criterion 4 (REQ-2618, REQ-2620). The rules are T1 to T7 of the `commit`
skill, and the README names them. `mise run all` passed with exit status 0.

## Left alone

A program that enforces these rules, because ADR-2420 states that review
holds them. Whether the harness supports a worktree manager at all, which
ADR-2420 leaves to ADR-2660.
