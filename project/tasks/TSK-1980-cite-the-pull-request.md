---
id: TSK-1980
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1320
closes: [REQ-3176]
issue:
---

# The record cites a pull request, never a commit hash

The record cites a pull request, never a commit hash, as ADR-1320 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a record gaining a line citing a check's revision by hash, when `check frozen` runs, then it reports the line. Closed by: a fixture.
2. Given the same line citing a pull request, when it runs, then it passes. Closed by: a fixture.

## What to do

In `meow-method check frozen`, report a line added since the base, outside the front matter, citing a hash of seven to forty hexadecimal digits after "at" or "revision". Change the verification's wording to cite the pull request.

## Depends on

Nothing. ADR-1320 is approved.

## Evidence

Not yet.

## Left alone

A version control tool other than git, which ADR-1320 leaves.
