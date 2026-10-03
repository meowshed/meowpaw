---
id: ADR-2540
artifact: adr
status: approved
revised: 2026-10-03
addresses:
  [
    REQ-1364,
    REQ-1366,
    REQ-1370,
    REQ-1390,
    REQ-1398,
    REQ-2562,
    REQ-2570,
    REQ-2584,
    REQ-2586,
    REQ-2588,
    REQ-2824,
  ]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2540. An epic projects onto a grouping the tracker offers, and the harness reports the links it made

## Decision

Where a tracker has a grouping, an epic projects onto it and its tasks onto
the items in it, and the grouping's description cites the authorising
record (REQ-1364). On GitHub the grouping is a parent issue with its tasks as
sub-issues, which extends the projection ADR-1310 decided. The projection is
a table of fields from record to tracker item, kept in the tracker's pack, so
a second tracker is a second table and not a second integration (REQ-1390).

The harness reports each link it made and the mechanism it used, and never
the status that will follow, because the mapping from an event to a status is
team configuration the harness can't see (REQ-2586). Where the grouping
doesn't close items on its own, the report says so (REQ-1366). Where a link
can't be made by the mechanism used, the report names it as not made
(REQ-1370). A pull request closes an item by keyword only where merging it
finishes the task, and references the item from any one part of a series
(REQ-2584). Where a tracker links by branch name, the branch carries the
tracker's identifier (REQ-2588).

A forge status reads as passing, failing or pending, never collapsed to two
(REQ-2570). A write the harness marks as its own doesn't start another
synchronisation, so the projection can't loop (REQ-1398). Where the client
offers a converted and a literal form of a field value, the pack names the
form it passes, and `gh` takes literal text with `--raw-field` (REQ-2562). A
pull request body states what changed in the terms of the requirement it
serves, why, and the evidence (REQ-2824), which prose rule S2 already asks of
every pull request this repository opens.

Once this is accepted, an approved epic shows on GitHub as one parent issue
with its tasks under it. What still doesn't work: there is no Linear pack, so
REQ-2588 holds for a tracker that links by branch only once one exists.

## Why

RES-0022 found that a tracker's grouping keeps an epic's tasks findable
together and that closing keywords inside a grouping behave differently per
tracker. RES-0133 found `gh` converts some field values unless told
otherwise and that a check's status has a pending state that tools often
fold into a failure. RES-0134 found Linear links an issue by the branch name
and maps events to statuses through team settings. RES-0025 found that a
synchronisation which reacts to its own writes loops.

## Alternatives

| Option                      | Better at             | Why it lost                                                    |
| --------------------------- | --------------------- | -------------------------------------------------------------- |
| Do nothing                  | No new projection     | An epic's tasks stay loose issues with no parent               |
| Milestones as the grouping  | Older and widely used | A milestone carries no description to cite the record from     |
| Report the resulting status | A fuller report       | The harness can't see the team's event mapping and would guess |

## What it costs

Each approved epic creates one more issue, and a repository with sub-issues
turned off loses the grouping, which the report says.

## What would reverse it

- GitHub withdraws sub-issues, or a tracker the harness supports has no
  grouping, which would leave the table with nothing to map onto.

## Consequences

`meow-github` gains the parent issue and sub-issue links and the three-valued
status. The projection's table moves into the pack's own file.

## How I will know it was realised

1. Projecting a fixture epic creates one parent issue citing the epic and one
   sub-issue per task (REQ-1364).
2. The report lists each link with its mechanism and no resulting status
   (REQ-2586, REQ-1370).
3. A pending check reads as `pending` (REQ-2570).
4. A write marked as the harness's own starts no second synchronisation in a
   fixture (REQ-1398).

## What this does not settle

- A Linear pack, or any second tracker.
