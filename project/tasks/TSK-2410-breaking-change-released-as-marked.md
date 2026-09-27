---
id: TSK-2410
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1540
closes: [REQ-3192]
issue:
---

# The release refuses a breaking change without the version showing it

What ADR-1570 decides for this part. One task, one branch, one pull request,
one review.

## Acceptance criteria

1. Given a unit whose commits since its last tag include one marked
   breaking, when the release check runs, then it refuses a patch bump,
   accepts a minor bump at zero and a major bump above zero. Closed by: tests
   naming REQ-3192, seen failing first.
2. Given a breaking commit touching `crates/meow/`, when the check runs, then
   it holds every unit that ships the binary. Closed by: a test naming
   REQ-3192.

## What to do

Add the check as a script under `tools/` with its tests, run by the `test` verb, and call it from `.github/workflows/release.yml` before packing.

## Depends on

Nothing. ADR-1570 is approved.

## Evidence

Not yet.

## Left alone

REQ-2532 and REQ-2544, which ADR-1570 postpones.
