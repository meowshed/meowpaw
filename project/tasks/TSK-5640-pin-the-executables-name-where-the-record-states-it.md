---
id: TSK-5640
artifact: task
status: approved
revised: 2026-10-11
realises: ADR-2920
closes: []
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Pin the executable's name where the record states it

The behaviour ADR-2920 decides already holds: the crate builds one binary
named `paw` (`default-run` in `crates/meow/Cargo.toml`), the launchers run it,
and SPC-1080 states the name. The task binds the decision to what holds the
behaviour, so the record names its plan (REQ-3902).

## Acceptance criteria

1. Given `crates/meow/Cargo.toml`, when a reader reads it, then the crate's
   binary is named `paw`. Closed by: `tools/test_shared_binary.py`, which
   resolves the binary at `plugins/meow-core/bin/<target>/paw`.
2. Given the specification, when a reader reads SPC-1080 "The native tool",
   then it states the crate builds one binary named `paw`. Closed by: the
   section's own text.

## What to do

Write the task's Evidence citing both. The behaviour and the specification
sentence already hold, and this task writes neither again.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

The Pi packages' `bin/paw` wrappers, which ADR-2920's own text covers and
SPC-1300 states.