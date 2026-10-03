---
id: ADR-2550
artifact: adr
status: approved
revised: 2026-10-03
addresses:
  [
    REQ-1810,
    REQ-1812,
    REQ-1814,
    REQ-1816,
    REQ-1818,
    REQ-1820,
    REQ-1822,
    REQ-1824,
    REQ-1826,
    REQ-1828,
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

# 2550. A task whose blocking dependency is unmerged stacks on its branch, built with `git` and `gh`

## Decision

A task opens its pull request against the trunk unless it names a blocking
dependency, in the sense ADR-1800 gave the word, whose pull request hasn't
merged. Such a task opens against that dependency's branch instead (REQ-1810,
REQ-1812). The stack's order is the dependency order the epic declares, and
no other (REQ-1814). An epic whose tasks block nothing is never stacked, and
the implement step says it declined (REQ-1840). A stack never crosses
repositories: where a dependency lives elsewhere, the step reports the stack
as impossible (REQ-1836).

The harness builds a stack with `git` and `gh` alone, so no stack tool is
needed, and the bases and links match what a stack tool would make
(REQ-1838). A task's pull request is found by its task identifier in the
branch name, never by a commit, so a rebase, split or reorder keeps the same
pull request and its reviews (REQ-1832, REQ-1834, REQ-1835). Git has no stable
change identifier, so the task identifier is the key.

After changing a pull request's base, the harness reads the base back from
the code host (REQ-1818) and reports the required checks as not run until
they run on the new base (REQ-1820). A check that passed on the old base is
never cited for the new one (REQ-1822). Where a restack stops part way, the
report names the branches updated and the ones not, and the step doesn't
repeat itself to cover the gap (REQ-1824). A conflict stops the restack and is
reported, with neither side discarded (REQ-1826). A force-push to a branch
with a pull request uses `--force-with-lease` against the revision last seen
(REQ-1828).

`paw status` names the layer of each stack that merges next and why each
layer above it can't (REQ-1816). Where a layer is closed or ejected, every
task above it reads as blocked by that layer (REQ-1830). A layer's review
reads that layer's diff against its own base and no more (REQ-1842). A
stacked task merges into the branch it targets and reaches the trunk once
every layer below it has merged (REQ-1844).

Once this is accepted, an epic with a chain of blocking tasks can open them
all at once and have each reviewed alone. What still doesn't work: this
repository's push guard denies a force-push, so a restack here waits until a
person allows a lease push, which a later decision has to settle.

## Why

RES-0065 found that stacked pull requests let a chain of dependent changes be
reviewed in parallel, and that every failure of a stack comes from a base
that changed without the tools noticing: a check run on an old base, a
mapping keyed by a commit a rebase replaced, a restack that half-finished. It
found that the stack tools all do the same few `git` and `gh` operations, so
a stack built by hand can match them. ADR-1800 already says whether a
dependency blocks.

## Alternatives

| Option               | Better at                 | Why it lost                                                    |
| -------------------- | ------------------------- | -------------------------------------------------------------- |
| Do nothing           | No stacks to keep         | A chain of blocking tasks waits for each merge in turn         |
| Require a stack tool | Restacking by one command | It makes a pack a dependency of the method, against REQ-0088   |
| Stack every epic     | One rule for every epic   | Stacking independent work adds ceremony and no review capacity |

## What it costs

A stack of three needs three reviews in order of merge, and a change to a low
layer restacks every layer above it, each with a fresh check run.

## What would reverse it

- The code host offers stacks natively with a stable identity per change,
  which would replace the hand-built bases.

## Consequences

The implement step's file gains the stacking rules. `paw status` gains the
next-to-merge line per stack. The `git` pack gains a restack that reports
each branch it updated.

## How I will know it was realised

1. A fixture epic with a blocking chain of three tasks opens three pull
   requests, each against the one below (REQ-1810, REQ-1814).
2. A fixture epic of independent tasks opens each against the trunk and says
   it declined to stack (REQ-1812, REQ-1840).
3. After a base change, the report names the checks as not run (REQ-1820).
4. A fixture restack with a conflict stops and names the branch (REQ-1826).
5. `paw status` names the next layer to merge (REQ-1816).

## What this does not settle

- Whether this repository's push guard allows a lease push for a restack.
- Merge queues beyond reporting an ejected layer.
