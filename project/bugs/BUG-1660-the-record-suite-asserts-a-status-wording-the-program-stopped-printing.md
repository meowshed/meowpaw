---
id: BUG-1660
artifact: bug
status: approved
severity: minor
violates: REQ-3074
enters: implement
found: 2026-10-11
revised: 2026-10-11
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The record suite carries a test that fails on the trunk, asserting a status wording the program stopped printing

`plugins/meow-flow`'s test suite fails on `origin/main`, so `mise run test` is
red on the trunk before any change of a session.

## Reproduction

Seen in an `origin/main` worktree, 2026-10-11, and on the trunk at
`6536d751`.

1. `git worktree add --detach <dir> origin/main`
2. `cd plugins/meow-flow && python3 -m unittest discover -s tests`
3. Read the failure: `test_a_rejected_provider_and_a_frozen_suspect_citation_are_reported`
   in `test_record.py`, asserting
   `"RES-0002, rejected, under 4 approved artifacts: ..."`.

## What the system does

The test fails on `origin/main` with `AssertionError`, asserting a line of
`paw status` output that no fixture in the test's repository produces. The
fixture expects a rejected provider under four approved artifacts; what the
program prints has drifted since the fixture was written, and no change of
this session causes it: the same suite fails in a clean `origin/main`
worktree.

## What it should do, and why

REQ-3074 says the trunk's gate passes, so a verification run records its
results against the tree it ran on. A suite red on the trunk makes every
pull request re-litigate a failure it did not cause, and the report of any
session mixes one inherited defect with its own work.

## Triage

`implement`: the fix is the test's fixture, aligning what it builds with what
the program prints, and nothing in the program. Minor: the trunk's test stage
is red, which costs every verification its binding, but the cause is a
fixture and the fix is one file.

## Closed by

The reproduction, now passing in a clean worktree of the trunk, in
`plugins/meow-flow/tests/test_record.py`.

## Tasks

- [x] T-001 Align the fixture of
      `test_a_rejected_provider_and_a_frozen_suspect_citation_are_reported`
      in `plugins/meow-flow/tests/test_record.py` with what `paw status`
      prints, and show the suite green in an `origin/main` worktree
      — done, then undone in the same pull request. The suite is green with
      the fixture as it was: a fresh build of the checker excludes a
      defect's `violates` from the provider walk (TSK-5500, ADR-2960), so it
      prints 4 approved artifacts, which is what the fixture asserted. The
      failure this defect records came from the installed `meow-core` 0.9.0
      binary the launchers prefer, which walks `violates` and prints 5
      (BUG-1680). The change to the fixture was reverted.
