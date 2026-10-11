---
id: BUG-1640
artifact: bug
status: approved
severity: minor
violates: REQ-0139
enters: implement
found: 2026-10-11
revised: 2026-10-11
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The record checker walks a defect's `violates` as a provider, so a withdrawal cascades into provenance chains

When a requirement a fixed defect once violated is withdrawn, every living
specification that reaches the defect through its descendants is flagged for
resting on the withdrawn requirement, because the provider walk follows the
defect's `violates` field as if the defect rested on the requirement it
accused.

## Reproduction

Seen at revision `a42e16d2` on this branch.

1. Withdraw a requirement that an approved defect's `violates` names, where an
   approved requirement elaborates the defect and a living specification
   states the requirement.
2. Run `paw check`.

## What the system does

The check reports the specification as resting on the withdrawn requirement
through the chain, and exits 1, although the specification depends on nothing
the withdrawal removed: the defect's link is the accusation that prompted the
requirement's descendants, not a dependency of the specification.

## What it should do, and why

REQ-0139 holds a living artifact to the providers it rests on, and a provider
is what a record depends on. The layout's own comment on `supersedes` and
`postpones` states the test: those relations name what a record moves away
from, not what it rests on. A defect's `violates` names what the defect moved
against, which is the same kind of link, so a withdrawal behind it is history
the specification carries, not a provider it depends on.

## Triage

It enters at implement: the walk's provider set is one line wide, and the fix
is the exclusion and its test. Severity is minor, because the check fails only
where a withdrawal meets this chain shape, and the failure blocks the gate
without pointing at anything to move.

## Closed by

The provider walk excludes `violates`, and a crate test holds it: a fixture
where a defect violates a withdrawn requirement and a living specification
states a requirement that elaborates the defect reports nothing.

## Tasks

- [ ] T-001 TSK-5500 exclude `violates` from the provider walk, in
      `crates/meow/src/record.rs`