---
id: TSK-1780
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1240
closes: [REQ-3010, REQ-3011]
issue:
---

# A retired name is recorded and never reused

A retired name is recorded and never reused, as ADR-1240 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a record carrying `unit:` or `status: proposed`, when `check front-matter` runs, then it reports the line and what replaced the name. Closed by: a fixture.
2. Given this repository, when `check front-matter` runs, then it reports nothing. Closed by: the check's output.

## What to do

Add a `[retired]` table to `lib/layout.toml` naming the retired field `unit` and statuses `proposed` and `current`, each with what replaced it. In `check front-matter`, report a record carrying a retired field or status, and a kind in the layout declaring one.

## Depends on

Nothing. ADR-1240 is approved.

## Evidence

Not yet.

## Left alone

A command that runs a migration, which ADR-1240 leaves.
