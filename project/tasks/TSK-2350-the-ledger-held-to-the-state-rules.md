---
id: TSK-2350
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1510
closes:
  [
    REQ-0752,
    REQ-0754,
    REQ-0756,
    REQ-0758,
    REQ-2958,
    REQ-2960,
    REQ-2962,
    REQ-2966,
    REQ-2967,
    REQ-2970,
  ]
issue: 548
projected: e38477c34117
---

# The ledger holds to the state rules

What ADR-1530 decides for this part, in the native tool's `verbs` feature, with its fixtures. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the fixtures ADR-1530's second criterion lists for identity, absent lines, the lock, pruning, purging, the environment switches, `state` and `evidence --all`, when they run, then each behaves as that criterion says. Closed by: fixtures naming each requirement, seen failing first.

## What to do

Change the native tool's `verbs` feature and its fixtures, state the change on `meow-verbs`' page, and move the unit to its next minor version where it hasn't moved since the last release.

## Depends on

TSK-2340, whose kept files the pruning leaves alone.

## Evidence

Not yet.

## Left alone

The other tasks of EPC-1510.
