---
id: TSK-5165
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2610
closes: [REQ-1426]
issue:
---

# Deny from a hook whose program is missing

Every blocking launcher denies and names its install command when its binary
is absent.

## Acceptance criteria

1. Given each launcher ADR-2710 names with its binary absent, the blocking
   hook denies with the install command and the stated non-blocking exception
   still allows. Closed by: launcher fixtures for REQ-1426.

## What to do

Share the missing-program response across the hook launchers.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

Programs invoked outside hooks.
