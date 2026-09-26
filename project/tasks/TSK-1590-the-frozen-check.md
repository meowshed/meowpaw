---
id: TSK-1590
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1170
closes: [REQ-0396, REQ-0398, REQ-0622, REQ-0626, REQ-0630, REQ-0634, REQ-0635]
issue:
---

# The frozen check

The frozen check, as ADR-1170 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given an approved requirement committed at `HEAD`, when its obligation is reworded, then `check frozen` exits 1 naming it. Closed by: a fixture.
2. Given the same rewording with an added `**Amended by ADR-0001.**` line, when `check frozen` runs, then it exits 0. Closed by: a fixture.
3. Given an approved task and an unverified epic, when evidence and a mark are added, then `check frozen` exits 0; given a verified epic, when a mark changes, then it exits 1. Closed by: fixtures.
4. Given a specification, when it is rewritten, then `check frozen` exits 0. Closed by: a fixture.

## What to do

Add `frozen` to `meow record check`, run only by name, with `--base <rev>` defaulting to `HEAD`. For each record approved at the base, read its text there with `git show`, compare it with the current file, and report a change outside what its kind may change, as SPC-1070 states, unless the change adds a line naming its authority. Run it in this repository's ship step against the trunk.

## Depends on

Nothing. ADR-1170 is approved.

## Evidence

Not yet.

## Left alone

Running the frozen check in continuous integration, which ADR-1170 leaves.
