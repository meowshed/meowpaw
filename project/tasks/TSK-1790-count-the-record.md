---
id: TSK-1790
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1240
closes: [REQ-3020]
issue: 310
---

# The record can be counted before and after a migration

The record can be counted before and after a migration, as ADR-1240 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a record, when `count` runs twice, then it prints each kind's count by status and the identifiers, identical both times. Closed by: a fixture.

## What to do

Add `meow-method count`, printing each kind's number of artifacts by status and the number of distinct identifiers, in a fixed order.

## Depends on

Nothing. ADR-1240 is approved.

## Evidence

Not yet.

## Left alone

A command that runs a migration, which ADR-1240 leaves.
