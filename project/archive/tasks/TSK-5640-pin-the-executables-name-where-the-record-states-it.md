---
id: TSK-5640
artifact: task
status: done
revised: 2026-10-11
realises: ADR-2920
closes: []
issue: 1115
projected: 1c8d642a3dfd
tracked: a77781331db9
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

Criterion 1 closes with `tools/test_shared_binary.py`, which resolves the
binary at `plugins/meow-core/bin/<target>/paw` and passes. Criterion 2
closes with SPC-1080's "The native tool" section, which states the crate
builds one binary, `paw`.

The five stages passed at tree `4364d882ff98`, each bound by `meow-checks run` and
confirmed by `meow-checks evidence`, exit 0: format `fcdc5ab700f0`, check
`c6bd6909315a`, lint `19fafec9381e`, test `fb6e4836449c`, build `a982d16b0043`.

## Left alone

The Pi packages' `bin/paw` wrappers, which ADR-2920's own text covers and
SPC-1300 states.
