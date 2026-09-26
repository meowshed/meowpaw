---
id: TSK-1620
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1180
closes: [REQ-0522, REQ-0523, REQ-0575, REQ-2870, REQ-2871, REQ-2872, REQ-2873]
issue:
---

# Generate each kind's index and check it for drift

Generate each kind's index and check it for drift, as ADR-1180 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a record whose decisions index holds a generated block, when a decision is added without `--write`, then `check index` exits 1 naming the index; when `index adr --write` runs, then it exits 0. Closed by: a fixture.
2. Given a kind of more than 36 requirements, when `index requirement` runs, then it prints the rows ordered by identifier and a view grouped by topic. Closed by: a fixture.
3. Given this repository, when its requirements index is migrated, then the count of requirements it lists equals the count of files before and after. Closed by: the counts in the evidence.

## What to do

Add `index <kind> [--write]` to `meow record` as SPC-1100 states it, and teach `check index` to report a generated block that differs from what `index` prints. Migrate `project/requirements/README.md` and `project/adrs/README.md` to generated blocks, as expand, migrate and contract, recording the count of entries before and after in the evidence.

## Depends on

Nothing. ADR-1180 is approved.

## Evidence

Not yet.

## Left alone

The research index and the project index, which ADR-1180 leaves as prose.
