---
id: TSK-1960
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1320
closes: [REQ-1312]
issue: 381
projected: a137b0a74372
---

# The sign-off names the commit's author

The sign-off names the commit's author, as ADR-1320 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a repository requiring the sign-off and a message signed off by someone other than the author, when `check-message` runs, then it reports the trailer naming both. Closed by: a fixture.

## What to do

In `meow-scm check-message`, where the profile's trailers include `Signed-off-by`, compare its value with the author identity `git var GIT_AUTHOR_IDENT` reports, and report a mismatch naming both.

## Depends on

Nothing. ADR-1320 is approved.

## Evidence

Not yet.

## Left alone

A version control tool other than git, which ADR-1320 leaves.
