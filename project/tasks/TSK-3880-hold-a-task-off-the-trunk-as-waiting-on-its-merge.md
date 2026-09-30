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

`OffTheTrunk` in `plugins/meow-flow/tests/test_record.py` holds nineteen checks, eleven
of them added with the two code reviews' fixes:
criteria 1 to 4 on fixture repositories with a declared trunk, none, no git
work tree, a trunk naming no branch and a remote-tracking trunk, and
criterion 5 on the method skill's rules read as a list. Seven failed at the
pull request's first commit; the eighth asserts that a finished task is never
held, which was true before. The gate's frozen check refused this task's own
`## Left alone`, which the template asks the implementer to fill, so the pull
request frees that section for a task, with a check in `Frozen`. `meow-checks run format lint check test` passed
all four verbs, and `meow-author check` reports 0 authoring failures.

## Left alone

The guard reads more than the requirement's word "absent": a task that is a
draft on the trunk and approved on the branch waits too, which is the case
ADR-2310's reasoning describes. `paw` reads the trunk on the remote named `origin` and no other, and a record
file with CRLF line endings on the trunk reads as not approved, as it did
before for any check. `steps/epic.md` needed no change: it names implement as the step after it, and
the method skill's M21 stops the one-pull-request path there. The `ready`
gate of the epic step on an unmerged decision has no program check, as
ADR-2310 says it doesn't settle.
