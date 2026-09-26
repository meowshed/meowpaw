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

The first half landed with issue #153. The marketplace reference documents a
hosted `marketplace.json` added by its `https://` address and an `archive`
source taking a zip by `url` and `sha256`, so SPC-1080 keeps its design and
now names the tags. `crates/meow/build-units x86_64-apple-darwin` cross-built
all three units on an ARM64 Mac, and `file` reports each binary as "Mach-O
64-bit executable x86_64". The pack step, run locally, packed all six units,
and `unzip -Z` on `meow-verbs-0.2.0.zip` lists both binaries and the launcher
with mode `-rwxr-xr-x`.

## Left alone

Signing the binaries.
