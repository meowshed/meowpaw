---
id: TSK-1830
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1250
closes: [REQ-3098, REQ-3180]
issue: 321
---

# An empty record reports its coverage as zero

An empty record reports its coverage as zero, as ADR-1250 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given an empty record, when `check coverage` and `status` run, then each says zero requirements and neither reads as complete. Closed by: a fixture.
2. Given REQ-3180, when its evidence is gathered, then the task records where each unit keeps what it keeps. Closed by: the evidence table.

## What to do

Make `check coverage` print how many requirements in force land in a task, `0 of 0` on an empty record, and make `status` say that an empty record's coverage is zero, not complete. Record the evidence that no unit writes into the repository to run itself.

## Depends on

Nothing. ADR-1250 is approved.

## Evidence

Not yet.

## Left alone

Onboarding from existing documents, which ADR-1250 leaves to the next
decision.
