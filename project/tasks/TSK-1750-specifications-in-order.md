---
id: TSK-1750
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1230
closes: [REQ-0525]
issue: 299
---

# The specifications read in citation order

The specifications read in citation order, as ADR-1230 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given an index listing a specification before one it cites, when `check index` runs, then it reports the pair. Closed by: a fixture.
2. Given this repository, when `check index` runs, then it reports nothing. Closed by: the check's output.

## What to do

In `check index`, for a living kind with a prefix, read the order in which its index first names each of its documents, and report a document named before one it cites. Remove the unit specifications' identifiers from SPC-1020, SPC-1030 and SPC-1080, naming the unit instead, and reorder the specifications in `project/README.md` so the check passes.

## Depends on

Nothing. ADR-1230 is approved.

## Evidence

Not yet.

## Left alone

Splitting approved requirements that carry two obligations, which ADR-1230
leaves to the amendment path.
