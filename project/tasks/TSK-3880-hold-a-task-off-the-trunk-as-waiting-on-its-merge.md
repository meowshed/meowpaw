---
id: TSK-3880
artifact: task
status: approved
revised: 2026-09-30
realises: ADR-2310
closes: [REQ-3656, REQ-3658, REQ-3660, REQ-3662, REQ-3664]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Hold a task off the trunk as waiting on its merge, and state where the one-pull-request path stops

`paw ready implement` refuses a task whose record isn't on the declared trunk,
`paw status` names it as waiting, and the method skill says when a decision's
records are written through to one pull request and how. One task, one
branch, one pull request, one review: the tests first, then the change, its
documentation and its marks.

## Acceptance criteria

1. Given a repository whose profile declares `[git] trunk`, with an approved
   task committed on a branch and absent from the trunk, when
   `paw ready implement <task>` runs, then it exits 1 naming the task and the
   trunk; given the same task on the trunk, then it exits 0. Closed by: a
   fixture test in `plugins/meow-flow/tests/test_record.py`.
2. Given the first fixture, when `paw status` runs, then it prints
   `waiting: <task> is not on <trunk> yet` and no `next: implement` for it;
   with the task on the trunk it prints `next: implement`. Closed by: a
   fixture test.
3. Given a profile with no `[git] trunk`, and given a directory that is no
   git work tree, when `paw ready implement` runs on an approved task, then
   it exits 0, and `paw status` prints one line saying an approval can't be
   told from one waiting on a merge. Closed by: a fixture test for each.
4. Given a trunk that exists only as a remote-tracking branch, when
   `paw ready implement` runs, then it reads that branch. Closed by: a
   fixture test.
5. Given `plugins/meow-flow/skills/method/SKILL.md`, when it is read, then M5
   opens with the exception and names M20, M20 opens with the person's
   request and names M5, a rule under M20 states that a record is written as
   a draft, checked, and set to `approved` only where `paw check` reports
   nothing, and that the path ends at the epic step, and rule identifiers run
   in order with none repeated. Closed by: a static test that reads the rules
   as a list.
6. Given this change's tree, when `meow-checks run format lint check test`
   runs, then each passes. Closed by: each verb's outcome in the task's pull
   request.

Each criterion is decidable from this task's own work.

## What to do

Change `ready` and `status` in `crates/meow/src/record.rs` to read the trunk
through git, and only for a task that is approved and open. Change the method
skill's steps and rules, `steps/epic.md` where it names the next step,
SPC-1090's Approvals and gate sections, `CLAUDE.md`'s `a_gate_is_a_stop`, and
the `meow-flow` page. Keep the method skill's core within `budget.toml`.
Raise `meow-flow`'s minor version, because `ready` refuses what it accepted.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

Not yet.
