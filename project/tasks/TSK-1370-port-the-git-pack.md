---
id: TSK-1370
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1080
closes: []
issue:
---

# Port the git pack to the native tool

One task, one branch, one pull request, one review.

## What to do

Port `meow-git`'s program to the `git` subcommand behind its feature, change its
launcher as SPC-1080 states, and delete `lib/meow_git.py`. The pack keeps
finding `meow-scm` where it is installed, now through that unit's launcher.

## Depends on

TSK-1350, which builds the crate and the shared module.

## Evidence

Not yet. The task closes on `meow-git`'s twelve fixtures, unchanged, passing
against the new launcher.

## Left alone

What the guards check, which SPC-1060 states.
