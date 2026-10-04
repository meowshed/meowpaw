---
id: ADR-2310
artifact: adr
status: done
revised: 2026-09-30
addresses: [REQ-3656, REQ-3658, REQ-3660, REQ-3662, REQ-3664]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2310. A decision a person asks for in one pull request is approved by its merge, and a task off the trunk isn't ready

## Decision

Where a person asks for a decision to land in one pull request, the method
skill writes its research, requirements, decision record, specification
changes, and its epic and tasks in turn, and stops once, at that pull request
(REQ-3656). Without the request it stops at every approval gate, as REQ-0390
says. This amends ADR-2300 in one respect: its sentence that these records
"land together in one pull request" holds where a person asks, and no longer
without condition.

On that path the skill writes each record as a draft, runs `paw check`, and
sets the record to `approved` only where the check reports nothing, so the
next step's gate passes (REQ-3658). Where the check still reports a finding
after two rounds, the skill stops there and reports it. The skill goes on
only as far as the epic step: it implements nothing on that path.

The program holds what the skill can't. `paw ready implement` refuses a task
whose record is absent from the trunk the profile declares under
`[git] trunk`, naming the task and the trunk (REQ-3660). It reads the
remote-tracking branch of that name where one exists and the local branch
otherwise. `paw status` prints `waiting: <task> is not on <trunk> yet` for
such a task in place of `next: implement` (REQ-3662). Where the profile
declares no trunk, the directory isn't a git work tree, or the trunk names no
branch, `ready` and `status` behave as before and `status` prints one line
saying an approval can't be told from one waiting on a merge (REQ-3664).

A record created on a branch stays free to edit until it lands, because
`check frozen` already skips a file absent at its base, so a person who asks
for changes on the pull request gets them as edits.

Once accepted, the record states the rule and nothing has changed in the
tree. Once the task lands, a task on an unmerged branch is never next, and
the skill states where it stops in both cases. What still doesn't work: a
repository that commits records straight to its trunk gets no guard, and
needs none, since nothing there is waiting on a merge.

## Why

The method skill held two rules that disagreed on where to stop, and the
program read an approved status on an unmerged branch as an approval:
`paw ready implement` exited 0 and `paw status` named the task next
(RES-0311). Records written as approved also skipped the rules the layout
applies to drafts alone (RES-0311). Rewording the rules twice left all three
in place (RES-0311), so the guard belongs to the program.

## Alternatives

| Option                                  | Better at                               | Why it lost                                                                                    |
| --------------------------------------- | --------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Do nothing                              | Costs nothing                           | A session picks one of two rules by chance, and implements before a merge                      |
| Drop the one-pull-request path          | Simplest to state, and every gate stops | Returns the cost RES-0310 measured, and the owner asked for the path                           |
| Store a status for "waiting on a merge" | Visible in the file itself              | A stored status somebody must move after the merge, where the merge already says it (RES-0311) |

## What it costs

`ready` and `status` read git, which the record program hasn't done outside
`check frozen`, so each run of them starts a process for every open task it
considers. A repository with a shallow clone or a renamed trunk gets the
"can't be told" line until its profile is right. A person who approves a task
by hand on a branch now has to merge it before implementing, which is the
point and is also one more step for a solo author.

## What would reverse it

- A repository in use whose records never reach a trunk, such as one with no
  branches, reporting the check as noise twice.
- Git reads making `paw status` take more than a second on this repository's
  record.

## Consequences

- ADR-2300 and REQ-0390 each gain a line naming this decision.
- The method skill's M5 and M20 name each other, and gain the draft, check,
  approve order and the stop at the epic step.
- SPC-1090's Approvals and gate sections state both, and `CLAUDE.md`'s
  `a_gate_is_a_stop` names the exception.
- `crates/meow/src/record.rs` gains the trunk read in `ready` and `status`.

## How I will know it was realised

1. On a fixture repository whose profile declares a trunk, with an approved
   task committed on a branch and absent from the trunk,
   `paw ready implement` exits 1 naming the task and the trunk, and exits 0
   once the task's file is on the trunk.
2. On the same fixture, `paw status` prints `waiting:` for that task and no
   `next: implement`, and prints `next: implement` once it is on the trunk.
3. On a fixture with no `[git] trunk`, and on one that is no git work tree,
   `paw ready implement` exits 0 and `paw status` prints the line saying an
   approval can't be told from one waiting on a merge.
4. The method skill's M5 opens with the exception and names M20, M20 opens
   with the person's request, and a rule under it states the draft, check,
   approve order and that nothing is implemented on that path.
5. Every requirement this decision addresses is named by a closed task.

## What this does not settle

- Whether a code host's own merge rules are read. The program reads the
  trunk's tree and nothing about who merged.
- The same guard for an epic step run on an unmerged decision. The skill's
  rule covers it, and no program check does.
