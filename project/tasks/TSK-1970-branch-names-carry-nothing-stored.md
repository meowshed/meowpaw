---
id: TSK-1970
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1320
closes: [REQ-2818]
issue: 382
projected: 1151b3b1d51b
---

# A branch name carries nothing the forge stores

A branch name carries nothing the forge stores, as ADR-1320 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a branch named with a date, or with the author's name, when `push-guard` runs, then it refuses the push naming the rule. Closed by: a fixture.

## What to do

In `meow-git push-guard`, refuse a push from a branch whose name holds a date, as four digits followed by a separator and two, or eight digits in a row, or the author's name as git reports it.

## Depends on

Nothing. ADR-1320 is approved.

## Evidence

Not yet.

## Left alone

A version control tool other than git, which ADR-1320 leaves.
