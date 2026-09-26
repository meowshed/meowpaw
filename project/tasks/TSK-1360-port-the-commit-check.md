---
id: TSK-1360
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1080
closes: []
issue:
---

# Port the commit check to the native tool

One task, one branch, one pull request, one review.

## What to do

Port `meow-scm`'s program to the `scm` subcommand behind its feature, change
its launcher as SPC-1080 states, and delete `lib/meow_scm.py`.

## Depends on

TSK-1350, which builds the crate and the shared module.

## Evidence

Not yet. The task closes on `meow-scm`'s fourteen fixtures, unchanged, passing
against the new launcher.

## Left alone

What the check checks, which SPC-1050 states.
