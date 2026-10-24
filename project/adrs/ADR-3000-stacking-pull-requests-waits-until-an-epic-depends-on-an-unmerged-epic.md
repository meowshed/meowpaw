---
id: ADR-3000
artifact: adr
status: approved
revised: 2026-10-24
addresses: []
postpones:
  [
    REQ-1810,
    REQ-1812,
    REQ-1814,
    REQ-1816,
    REQ-1818,
    REQ-1820,
    REQ-1822,
    REQ-1830,
    REQ-1832,
    REQ-1834,
    REQ-1835,
    REQ-1836,
    REQ-1838,
    REQ-1840,
    REQ-1842,
    REQ-1844,
  ]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 3000. Stacking pull requests waits until an epic depends on an unmerged epic

## Decision

I postpone sixteen of the requirements ADR-2550 addressed, REQ-1810 to
REQ-1844, which govern a task's pull request stacked on the pull request of a
task it depends on, and so amend ADR-2550 in that respect. I withdraw TSK-4660, TSK-4670 and TSK-4690,
which would have built the rules. TSK-4680 stays done, and the three
requirements it closed stay closed.
ADR-2860 makes an epic one branch, one pull request and one review, with its
tasks as groups of commits on that branch, and its alternatives reject one
pull request for each task, stacked. A task therefore never has a pull request
to stack on, and the rules of ADR-2550 for task layers have no subject.

`meow-git restack` stays, with REQ-1824, REQ-1826 and REQ-1828, which TSK-4680
closed. It rebuilds any list of branches from the bottom up and needs no
task-level stack to be useful. An epic that depends on an unmerged epic waits
for that epic's merge. SPC-1090 loses its section on stacked tasks and the
`paw status` lines for stacks, because it described a flow the constitution
forbids.

Once this is accepted, the record stops asking for task layers, `paw status`
prints no `next:` for EPC-2430, and the sixteen requirements read as postponed.
What still doesn't work: two epics can't be under review together while one
builds on the other.

## Why

ADR-2860 chose the single pull request for an epic because a stop at the
records cost EPC-2760 three more pull requests and about 18 minutes of gate
time without a reviewer reading less (RES-0346). A stack of task pull
requests brings the cost back with extra work of its own: a base to read back
after each change, each required check to rerun on the new base, and a layer
to restack when the one below it merges.

## Alternatives

| Option                                   | Better at                            | Why it lost                                                                                                                              |
| ---------------------------------------- | ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Do nothing                               | Keeps ADR-2550 whole                 | Leaves sixteen requirements and three tasks that contradict ADR-2860, and a specification that describes a flow the constitution forbids |
| Stack epics now                          | Reviews two dependent epics together | No epic in this repository has waited on an unmerged one, so I would build for a case it hasn't met                                      |
| Rewrite the three tasks as epic stacking | Keeps the tasks and the requirements | The requirements name tasks, layers and task identifiers in branch names, so each would need rewording first                             |

## What it costs

A dependent epic waits for the merge of the epic it builds on, and the owner
merges epics in order. The stack tooling that ADR-2550 described is not built.

## What would reverse it

- An epic's work is blocked on an unmerged epic twice, or the owner asks to
  review dependent epics together.

## Consequences

Sixteen requirements read as postponed under Postponed in `paw status`.
TSK-4660, TSK-4670 and TSK-4690 are withdrawn, and EPC-2430 closes with one
task done. SPC-1090 and SPC-1060 stop describing stacked tasks.

## How I will know it was realised

1. `paw status` lists the sixteen under Postponed and names no `next:` for
   EPC-2430.
2. `paw check` reports no finding, and no specification describes a stacked
   task.

## What this does not settle

- Stacking whole epics, which a later decision takes up when its condition
  holds.
