---
id: ADR-2960
artifact: adr
status: done
revised: 2026-10-11
addresses: [REQ-0139]
supersedes: []
---

# 2960. A defect names what it moved against, and the provider walk follows no violation

## Decision

The record checker's provider walk treats a defect's `violates` relation as
what the defect moved against, not what it rests on: `violates` joins
`supersedes` and `postpones` in the walk's exclusions (REQ-0139). A
requirement a defect once violated can be withdrawn without flagging every
living specification that reaches the defect through its descendants, because
the specification depends on nothing the withdrawal removed.

## Why

The walk's own comment states the test the exclusion applies: the relations it
already excludes name what a record moves away from, not what it rests on. A
violation is the third link of that kind — the defect accuses the requirement,
and the record the defect prompted carries the accusation as provenance. The
chain the walk drew through it reported this repository's own specification as
resting on a withdrawn requirement (BUG-1640), where nothing the withdrawal
removed was a dependency of anything.

## What would reverse it

- If a living artifact's only path to a requirement it truly depends on runs
  through a defect's `violates`, the exclusion would hide a real rest, and I
  would restore the relation to the walk and move the provenance instead.

## Alternatives

| Option                                                                     | Better at                              | Why it lost                                                                                                                                       |
| -------------------------------------------------------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Move the provenance instead: amend the frozen records that cite the defect | Keeps the walk's provider set as it is | The records the chain runs through are approved and frozen, so the move rewords what approval froze                                               |
| Leave the withdrawal out and keep the requirement in force                 | No checker change                      | The requirement names a mapping for an agent the harness no longer ships, and a false requirement in force is the drift the record exists to stop |

## What it costs

A living artifact whose only path to a requirement it truly depends on runs
through a defect's `violates` is no longer flagged for resting on it, so the
walk trades one real finding for the false ones the exclusion removes.

## Consequences

- `crates/meow/src/record.rs` excludes `violates` from the walk, with the
  reason beside its neighbours, and a crate test holds both halves.
- The status report that reads rejected providers through the same walk moves
  with it, so an approved artifact is no longer reported as resting on a
  rejected requirement through a defect's accusation.

## How I will know it was realised

1. The fixture in TSK-5500's first criterion reports nothing.
2. The second still reports a draft, so the exclusion hides no draft finding.

## What this does not settle

- Whether any other relation names what a record moved against, which waits
  for a case.
