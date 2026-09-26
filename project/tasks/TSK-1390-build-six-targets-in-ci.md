---
id: TSK-1390
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1080
closes: []
issue:
---

# Build the crate for all six targets in continuous integration

One task, one branch, one pull request, one review.

## What to do

Move the six-target build out of `.github/workflows/release.yml` into
`.github/workflows/build.yml`, which CI runs on every pull request and push
that changes the crate, a unit's launcher or the build itself, and which the
release calls for the binaries it packs. One matrix then serves both, so the
release never builds a target that CI hasn't.

## Why it was added

EPC-1080's second criterion asks for the crate to build for all six targets in
continuous integration. The verification under issue 160 found that only the
release, run by hand, built them, and that the gate builds one target. Nobody
foresaw it because TSK-1380 put the matrix in the release and the plan read
that as CI.

## Depends on

TSK-1380, because it moves the matrix that task wrote.

## Evidence

Not yet.

## Left alone

The gate's own `crate` task, which still runs the crate's tests for one target.
