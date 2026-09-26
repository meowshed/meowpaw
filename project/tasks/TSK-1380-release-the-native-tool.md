---
id: TSK-1380
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1080
closes: [REQ-0074, REQ-3178]
issue:
---

# Release the units with their binaries

One task, one branch, one pull request, one review.

## What to do

Confirm first that a marketplace can be added from a released file's address,
and change SPC-1080 if it can't. Then write `.github/workflows/release.yml`:
build all six targets for each unit that changed, pack each unit with its
binaries as an archive, and publish the archives with their SHA-256, their
sizes and a marketplace file pointing at them by `url` and `sha256`. Each
unit's archive carries its own version (REQ-0074), and a person installs it
with nothing else (REQ-3178).

## Depends on

TSK-1350, TSK-1360 and TSK-1370, because a release carries every ported unit.

## Evidence

Not yet. The task closes on a release published from the workflow, every
target built, each archive's size in the release, and one unit installed from
it on a machine with neither Python nor Node.js.

## Left alone

Signing the binaries.
