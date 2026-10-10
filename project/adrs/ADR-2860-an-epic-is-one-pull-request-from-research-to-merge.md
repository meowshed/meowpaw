---
id: ADR-2860
artifact: adr
status: approved
revised: 2026-10-10
addresses:
  [
    REQ-4400,
    REQ-4402,
    REQ-4404,
    REQ-4406,
    REQ-4408,
    REQ-4410,
    REQ-4412,
    REQ-4414,
  ]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2860. An epic is one pull request, from its research to the merge of its completed work

## Decision

The work of one epic that a person asks for is one branch, one pull request and
one review (REQ-4400). It takes either of two forms, and both stay possible. In
the first, a person asks for the epic and the work runs from its research to the
merge of its completed work, in one pull request (REQ-4410). In the second, the
epic's records are already approved on the trunk, from an earlier pull request,
and a person asks for its work, which the method skill implements on one branch
in one pull request (REQ-4414). A person who asks only for a decision still gets
its records in one pull request, as ADR-2310 says (REQ-3656). A defect that
carries its tasks, and a task that realises a decision with no epic, follow the
same rule from their record to the merge of their fix (REQ-4402, REQ-4404). The
tasks of an epic are groups of commits on that branch, each with its tests
first, and each is marked in the commit that completes it.

In the first form the skill writes the research, the requirements, the
decision, the specification changes, the epic and the tasks, implements the
tasks on the same branch, and stops once, at the pull request. It still writes
each record as a draft, runs `paw check`, and sets a record to `approved` only
where the check reports nothing (REQ-3658, from ADR-2310). The merge is the one approval, and
what the skill implemented before it is at risk of rejection with the decision.
I accept that risk, because a stop at the records cost EPC-2760 three more pull
requests and about 18 minutes of gate time without a reviewer reading less
(RES-0346).

`paw ready implement` reads a task's approval from the working tree, so a task
approved on the epic's own branch is ready (REQ-4412). The guard that read it
from the trunk, and the status line that named a task waiting on its merge, are
withdrawn (REQ-3660, REQ-3662, REQ-3664), so ADR-2310 is amended in that
respect and holds in the rest.

An epic whose pull request would not be one reviewable change is split into
smaller epics before its work starts, and the pull request is never split in
its place (REQ-4406). An epic or a defect with no unmerged dependency opens its
pull request against the trunk (REQ-4408).

Once this is accepted, a person gets an epic's whole cycle, or the work of a
prepared epic, in one pull request.
What still doesn't work: stacking an epic on an unmerged epic names tasks in
its tooling (ADR-2550), and I haven't changed that.

## Why

RES-0346 found that epics hold 2.7 tasks on average, so one pull request for
each task, plus one for the records, multiplies the gate and the merges for
the same commits, and the second form keeps the records reviewed apart where a
person wants them so. The commit skill's own bound, split a branch that has grown
past one reviewable change, becomes a bound on the epic, which is where the
size is decided.

## Alternatives

| Option                                           | Better at                                       | Why it lost                                                              |
| ------------------------------------------------ | ----------------------------------------------- | ------------------------------------------------------------------------ |
| Do nothing                                       | Smallest reviews, a guard against self-approval | A gate run and a merge for each task and for the records, 3.7 on average |
| One pull request for each task, stacked          | Small reviews and ordered tasks                 | Tooling for stacks, and a merge for each, which is the cost              |
| One epic, records first, then the implementation | Nothing implemented on a rejected decision      | Two pull requests for one change, and the guard that holds them          |
| One epic, one pull request                       | One gate, one review, one merge                 | Larger reviews, and work done on a decision that may be rejected         |

## What it costs

A rejected decision costs its implementation as well, and a larger pull
request is easier to approve than to read. The split valve of REQ-4406 is the
only bound on that, and it is a judgement of the person who sizes the epic.
A task approved by the agent that implements it is no longer refused by the
tool, so the merge is the only thing between a self-approved task and the
trunk.

## What would reverse it

- Two epics whose pull requests were merged and later found to have been
  approved without a reading, or a rejected epic whose implementation cost more
  than the pull requests it saved. While neither is recorded, the saving stands.

## Consequences

REQ-1296, REQ-1812, REQ-3660, REQ-3662 and REQ-3664 are withdrawn and replaced,
and ADR-2310 is amended: its stop at the records stays, and its guard goes. SPC-1060 and SPC-1090 state the rule.
EPC-2770 carries three tasks: the readiness read, the constitution and the
method unit's text, and the commit skill.

## How I will know it was realised

1. `paw ready implement` exits 0 for a task approved on the working tree and
   absent from the trunk (REQ-4412).
2. No living or shipped text says "one task, one branch, one pull request", and
   `CLAUDE.md` says that an epic is one pull request (REQ-4400).
3. EPC-2770 itself merged as one pull request holding its records and its
   three tasks.

## What this does not settle

- Stacking an epic on another epic's unmerged branch, whose tooling names
  tasks (ADR-2550).
- Who sizes an epic: REQ-4406 asks for the split and names no measure.
