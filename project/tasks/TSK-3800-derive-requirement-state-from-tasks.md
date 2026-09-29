---
id: TSK-3800
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-2200
closes:
  [
    REQ-3600,
    REQ-3602,
    REQ-3604,
    REQ-3608,
    REQ-3610,
    REQ-3620,
    REQ-3622,
    REQ-3646,
    REQ-3648,
  ]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Derive each requirement's state from the tasks, epics and defects that name it

`paw` derives a requirement as closed when a closed task or epic names it and no open one does, open while an open defect names it, and open when nothing names it, with no verified state. `status` names no step whose work has landed and lists each postponement with its condition, and coverage accepts any number of tasks per requirement. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given a fixture requirement whose only task is marked `[x]`, when `paw show` runs, then it reports the requirement closed and prints no `verified`. Closed by: a `meow-flow` fixture test.
2. Given a requirement named by two tasks, one open, when `paw show` runs, then it reports the requirement open. Closed by: a fixture test.
3. Given a closed requirement that an open defect names in `violates`, when `paw show` runs, then it reports the requirement open. Closed by: a fixture test.
4. Given one task naming three requirements and one requirement named by two tasks, when `paw check coverage` runs, then it reports nothing. Closed by: a fixture test.
5. Given an approved decision postponing a requirement, when `paw status` runs, then it lists that requirement with the decision's reversal condition. Closed by: a fixture test.
6. Given an epic whose tasks are all done and no `checked-at`, when `paw status` runs, then it reports the epic closed and names no `document` or `verify` step. Closed by: a fixture test.

## What to do

Change `crates/meow/src/record.rs`: the state derivation, `show`, `status` and the coverage rule. Remove the rules that read `checked-at` and the verified count; the field stays readable on old epics and means nothing. Keep `status` output stable across two runs.

## Depends on

Nothing.

## Cover

Not yet. The cover step replaces this line with four, `Checks`,
`Failing run`, `Landed in` and `Judgement`, and `paw ready implement` refuses
the task until they are filled.

## Evidence

Not yet.

## Left alone

The in-flight worktrees for TSK-2703, TSK-2950, TSK-3350 and TSK-3700 are
postponed by the owner and left as they are.
