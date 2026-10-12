---
id: TSK-5170
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2615
closes: [REQ-2992]
issue: 1014
projected: 4615300fd583
tracked: c390db8c2740
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

Criterion 1 closes with the generator and drift fixtures in
`crates/meow/src/interface.rs`: the drift test
`the_committed_page_is_current` fails a stale page, and
`a_key_without_a_comment_fails_the_page` names a key whose documentation
comment is empty (REQ-2992).

## Left alone

Narrative guides.
