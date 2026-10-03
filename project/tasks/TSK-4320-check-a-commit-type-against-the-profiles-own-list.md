---
id: TSK-4320
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2320
closes: [REQ-2952]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Check a commit type against the profile's own list

`meow-scm check-message` accepts a type only where the profile's
`[commits.types]` declares it, and holds no list of types of its own, as
SPC-1050 states. One task, one branch, one pull request, one review: the
tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a profile whose `[commits.types]` declares `spec` and `chore` only,
   when `check-message` reads `feat: add a verb`, then it reports the
   `declared type` check failed and exits 1 (REQ-2952). Closed by: a crate
   test naming REQ-2952, seen failing first or, where it passes before the
   change, cited as the test that holds the rule.
2. Given the same profile, when `check-message` reads `spec: state the
profile`, then it reports no violation of the type check (REQ-2952).
   Closed by: a crate test naming REQ-2952.
3. Given the `scm` feature's source, when a test searches it, then it finds
   no list of conventional types the type check reads. Closed by: a crate
   test naming REQ-2952.

## What to do

Read the type check in the `scm` feature of `crates/meow/` and confirm it
reads `[commits.types]` alone. Where any built-in list feeds it, remove that
path. Where none does, the tests above pin the behaviour, because ADR-2370
asks that the rule be held by a test and the tree may already meet it.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

The attribution check, which runs whatever the profile says, and the
undeclared convention, which keeps exit 3 as SPC-1050 states.
