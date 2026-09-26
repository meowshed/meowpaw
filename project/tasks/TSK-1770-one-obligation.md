---
id: TSK-1770
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1230
closes: [REQ-2880]
issue:
---

# A draft requirement carries one obligation, stands alone, and prohibits with MUST NOT

A draft requirement carries one obligation, stands alone, and prohibits with MUST NOT, as ADR-1230 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a draft requirement with two keywords, one leaning on a neighbour, and one negating a requirement, when `check rules` runs, then it reports each. Closed by: a fixture.
2. Given the same statements in an approved requirement, when `check rules` runs, then it reports nothing. Closed by: a fixture.

## What to do

Add the draft rules `one-obligation`, `stands-alone` and `no-negated-requirement` for the requirement kind, reading the paragraph under the heading.

## Depends on

Nothing. ADR-1230 is approved.

## Evidence

Not yet.

## Left alone

Splitting approved requirements that carry two obligations, which ADR-1230
leaves to the amendment path.
