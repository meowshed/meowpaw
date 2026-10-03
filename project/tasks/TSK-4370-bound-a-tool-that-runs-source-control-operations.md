---
id: TSK-4370
artifact: task
status: approved
revised: 2026-10-03
realises: ADR-2420
closes: [REQ-2608, REQ-2610, REQ-2612, REQ-2614, REQ-2616, REQ-2618, REQ-2620]
issue:
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

Not yet.

## Left alone

A program that enforces these rules, because ADR-2420 states that review
holds them. Whether the harness supports a worktree manager at all, which
ADR-2420 leaves to ADR-2660.
