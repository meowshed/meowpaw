---
id: TSK-5150
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2590
closes: [REQ-1420, REQ-1422]
issue:
---

# Require a fresh prompt for each attended irreversible action

Permission hooks and the method require one confirmation for each attended
push, merge, release, issue write or governance change.

## Acceptance criteria

1. Given each named operation in an attended fixture, when it is invoked,
   then the hook asks before allowing it. Closed by: hook fixtures for
   REQ-1420.
2. Given one allowed operation followed by another, when the second is
   invoked, then it asks again. Closed by: a two-invocation fixture for
   REQ-1422.
3. Given a read, a repository-local write or an unattended run, when the same
   hooks evaluate it, then this rule adds no prompt. Closed by: negative hook
   fixtures.

## What to do

Name the operations in the relevant hook units and method step, request no
reusable prefix for them, and keep ADR-2380's unattended path separate.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

The platform's own prompt text and unattended authority.
