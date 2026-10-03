---
id: ADR-2690
artifact: adr
status: approved
revised: 2026-10-03
addresses: [REQ-1660, REQ-1662, REQ-1666, REQ-1668, REQ-1670]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2690. The harness is held to its own method, and the six source repositories test it

## Decision

The harness is developed by its own method in this repository, with its
record in the layout it gives its users, written by the same steps and held
to the same checks (REQ-1660, REQ-1668). This already holds: `project/` is the
record, `.meowpaw/profile.toml` declares it, and `paw check` runs in the gate.
The task for each is a test that fails if the record leaves the layout
`paw template` prints.

Every requirement declares one of the four kinds of check ADR-1510 named,
static, behavioural, evaluation or judgement, and `paw check` already fails
one whose `verification` names any other kind (REQ-1662). Where the harness's own work needs a
capability it doesn't have, the step writes a defect or a postponement, and
never works around the gap in silence (REQ-1670).

The six private harnesses RES-0002 describes migrate onto the harness one at
a time, and each migration is an evaluation: the repository's own gate runs
before and after, and a behaviour it relied on that stops working is a defect
against this harness (REQ-1666). The order is from the smallest repository
to the largest, and the evaluation runs by hand, as the owner's rule for
model calls asks.

Once this is accepted, the vision's test of success, the six repositories
dropping their private copies, has a decision behind it. What still doesn't
work: none of the six has migrated, so REQ-1666 stays unproven until the
first does.

## Why

RES-0001 found that a method its authors exempt themselves from has
disproved itself before it ships, which CLAUDE.md's `own_method_first`
repeats. RES-0002 found the six harnesses each carry behaviour their owners
rely on, so a migration that loses any of it fails the vision's test.
RES-0005 and RES-0070 found that a requirement nobody can check is a wish.

## Alternatives

| Option                      | Better at               | Why it lost                                                           |
| --------------------------- | ----------------------- | --------------------------------------------------------------------- |
| Do nothing                  | No migration work       | The vision's one test of success is never run                         |
| Migrate all six at once     | One evaluation pass     | A defect found in the first would repeat in the other five            |
| A synthetic test repository | No real project at risk | It shows the harness works on what it was written for, not on the six |

## What it costs

Each migration takes a repository's owner time to compare before and after,
and a defect found stops the next migration until it is fixed.

## What would reverse it

- A migration shows a behaviour the harness can't carry without a language
  named in the method, which would put REQ-1666 against REQ-0070.

## Consequences

The crate gains a test that the record follows the layout. Each migration is
a task with its evaluation recorded as its evidence.

## How I will know it was realised

1. A test fails when a record file sits outside the layout `paw template`
   prints (REQ-1668).
2. The first of the six repositories runs its gate green after migrating, and
   its evaluation is the task's evidence (REQ-1666).

## What this does not settle

- REQ-3034, which asks that the measurement suite run on a schedule. The
  owner keeps model calls out of CI and runs evaluations by hand, so the two
  disagree and a later decision has to withdraw one.
