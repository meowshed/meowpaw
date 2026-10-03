---
id: TSK-4660
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2430
closes:
  [
    REQ-1810,
    REQ-1812,
    REQ-1814,
    REQ-1832,
    REQ-1834,
    REQ-1835,
    REQ-1836,
    REQ-1838,
    REQ-1840,
    REQ-1844,
  ]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Open a stack in the implement step

The implement step opens a task's pull request against its unmerged blocking
dependency's branch, in the epic's dependency order, with `git` and `gh`
alone, and against the trunk otherwise, as SPC-1090 states under "Stacked
tasks". One task, one branch, one pull request, one review: the tests first,
then the change, its documentation and its marks.

## Acceptance criteria

1. Given `steps/implement.md`, when a fixture reads it, then it names a
   blocking dependency with an unmerged pull request as the one condition for
   `gh pr create --base <dependency's branch>`, and the trunk as the base
   otherwise (REQ-1810, REQ-1812). Closed by: a fixture under
   `plugins/meow-flow/tests/` naming both, seen failing first.
2. Given the same file, when the fixture reads it, then it takes the stack's
   order from the blocking dependencies alone, says a `(not blocking)` line
   never stacks, and says the step reports declining to stack an epic whose
   tasks block none of each other (REQ-1814, REQ-1840). Closed by: the same
   fixture.
3. Given the same file, when the fixture reads it, then it names the task's
   identifier in the branch name as the key to its pull request and forbids a
   commit as the key (REQ-1832, REQ-1834, REQ-1835). Closed by: the same
   fixture.
4. Given the same file, when the fixture reads it, then it reports a stack
   across repositories as impossible and opens nothing, and names the bottom
   layer as the one that merges first (REQ-1836, REQ-1844). Closed by: the
   same fixture.
5. Given a model following the step on a fixture epic with three blocking
   tasks, when a reviewer reads the commands it would run, then they are `git`
   and `gh` commands only and give each layer the base and the body links a
   stack tool would (REQ-1838). Closed by: judgement in the pull request's
   review, because the gate makes no model calls.

## What to do

Add the stacking rules to `plugins/meow-flow/skills/method/steps/implement.md`
as labelled rules in the unit's prompt form, held to SPC-1030 and the unit's
`budget.toml`: when to stack, the order, the branch name carrying the task's
identifier in lower case, the body links to the layers below and above, the
cross-repository refusal, and merging from the bottom with the person doing
each merge. Say that `ready implement` runs on the dependency's branch, where
its Evidence is written. Name no tool beyond `git` and `gh`.

Document stacking on `plugins/meow-flow/README.md`.

## Depends on

Nothing.

## Evidence

Not yet.

Criterion 5 rests on judgement, for the reason it gives.

## Left alone

Reading a changed base back and reviewing one layer, which TSK-4670 adds to
the same file, and the restack program, which TSK-4680 adds to `meow-git`.
