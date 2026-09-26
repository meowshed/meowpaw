---
id: TSK-1640
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1180
closes: [REQ-0636, REQ-1600, REQ-1601, REQ-1602, REQ-1604, REQ-1606, REQ-1608]
issue: 254
---

# Search the record, and search it first

Search the record, and search it first, as ADR-1180 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a record, when `find approval gate` runs, then it prints identifier and heading lines ranked by the words matched, at most twenty, and no body text. Closed by: a fixture.
2. Given the `method` skill, when the prompt check runs, then it passes and the rules block carries the three rules. Closed by: the check's output and the labels.

## What to do

Add `find <word>...` to `meow record` as SPC-1100 states it, and add rules to the `method` skill: search the record with `find` before writing, follow or amend a decision found, and write a durable finding back into an artifact, each with its reason.

## Depends on

Nothing. ADR-1180 is approved.

## Evidence

Not yet.

## Left alone

The research index and the project index, which ADR-1180 leaves as prose.
