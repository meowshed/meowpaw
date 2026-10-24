---
id: TSK-5684
artifact: task
status: approved
revised: 2026-10-24
epic: EPC-2850
closes: [REQ-4510]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Resolve a launcher's binary once per machine

A unit's launcher walks the core unit's data directory on every guarded call. It resolves the path once, keeps it, and reuses it.

## Acceptance criteria

1. Given a launcher run twice on one machine, when the second run starts, then it reads the resolved path from a file under its data directory and does not probe the machine or walk the core unit's data directory (REQ-4510). Closed by: a test with stand-ins for `uname` and the directory walk that counts each probe and sees it run once, seen failing against the launcher before the change.
2. Given a cached path whose binary no longer exists, when the launcher runs, then it resolves again, replaces the cache and runs the new binary (REQ-4510). Closed by: a test that deletes the binary between two runs.
3. Given the generated launchers of every unit, when `mise run all` runs, then it exits 0 (REQ-4510). Closed by: the gate of the pull request that carries this task.

## What to do

Add the resolution to the launcher template TSK-5683 writes, so every unit's launcher carries it, and regenerate them. The cache lives under the unit's data directory the platform provides, and a missing or unreadable cache means resolve again.

## Depends on

- TSK-5683 (blocking): the launcher template this task extends is the one that task writes.

## Evidence

Not yet.

## Left alone

The hook that starts a session, and what the launcher does after it has found its binary.
