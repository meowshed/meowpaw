---
id: TSK-1500
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1150
closes:
  [
    REQ-0237,
    REQ-0638,
    REQ-0640,
    REQ-0642,
    REQ-0644,
    REQ-0646,
    REQ-0648,
    REQ-0650,
    REQ-0652,
    REQ-0654,
    REQ-0658,
  ]
issue:
---

# Resolve an identifier and what cites it

One task, one branch, one pull request, one review.

## What to do

Add `meow record show <id>` as SPC-1100 states it: the artifact's path, kind, stored status, title and first paragraph, its own relation fields under `Names`, and under `Cited by` every artifact whose relation fields name it, grouped by field, and every other file in the record that mentions it under `body`. Exit 1 for an identifier that resolves to nothing. Write fixtures for `show`, for a withdrawn artifact resolving, and for each relation rule ADR-1150 records as held: bare identifiers, the fixed vocabulary, the upward direction and every relation resolving, each seen failing first against a program that returns nothing.

## Depends on

Nothing. ADR-1150 and SPC-1100 are approved.

## Evidence

Not yet.

## Left alone

Checks and tests outside the record that name a requirement.
