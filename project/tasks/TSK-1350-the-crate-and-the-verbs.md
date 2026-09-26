---
id: TSK-1350
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1080
closes: [REQ-0032, REQ-0076]
issue: 150 151 152 153
---

# Build the crate, and run the verbs on it

One task, one branch, one pull request, one review.

## What to do

Create `crates/meow/` as SPC-1080 states: one binary, a feature per unit, and a
shared module for the profile, the report shapes and the exit codes (REQ-0076).
Port `meow-verbs`' program to the `verbs` subcommand, change its launcher to
pick `bin/<target>/meow` and report every verb unrun where there is none, and
delete `lib/meow_verbs.py`. Add `mise run build` for the local build, ignore the
binaries, and run the crate's tests in the gate.

Keep the tool's record and tracker features out of every step the units run,
so each unit is complete without them (REQ-0032).

## Depends on

Nothing. ADR-1110 and SPC-1080 are approved. Building on this machine needs
the Xcode licence accepted.

## Evidence

Not yet. The task closes on `meow-verbs`' twelve fixtures, unchanged, passing
against the new launcher, and on the crate's own tests passing.

## Left alone

The other units' programs, and the release.
