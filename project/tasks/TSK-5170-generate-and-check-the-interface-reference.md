---
id: TSK-5170
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2615
closes: [REQ-2992]
issue:
---

# Generate and check the interface reference

Generate the public interface page from documentation comments and fail drift.

## Acceptance criteria

1. Given ADR-2720's subcommand and profile-key changes, the generator updates
   all six interface parts and the check fails stale output. Closed by:
   generator and drift fixtures for REQ-2992.

## What to do

Implement the generator, generated page and check in one task.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

Narrative guides.
