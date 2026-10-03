---
id: TSK-5160
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2605
closes: [REQ-2716, REQ-2727, REQ-2728]
issue:
---

# Hold the prose gate's network exception

Hold every hook to no network except the prose gate's bounded judge, and
advance the revision for failed tool attempts too.

## Acceptance criteria

1. Given ADR-2700's hook fixtures, only the bounded prose judge passes and
   every attempted tool use advances the revision. Closed by: author and hook
   fixtures for REQ-2716, REQ-2727 and REQ-2728.

## What to do

Implement the exception in `meow-author check` and the hook subcommands.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

Non-hook commands.
