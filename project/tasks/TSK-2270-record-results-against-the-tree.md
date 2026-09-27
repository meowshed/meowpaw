---
id: TSK-2270
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1460
closes: [REQ-0146]
issue:
---

# `meow-verbs run` records each result against its tree id, and `meow-verbs evidence` reports it

`run` appends a record per verb to a ledger outside the repository, bound to
the tree id before and after the verb, and `evidence` reports whether each
verb's latest record holds for the current tree. One task, one branch, one
pull request, one review.

## Acceptance criteria

1. Given a repository declaring a passing, a failing and no command for three
   verbs, when `run` runs all three, then the ledger under the fixture's
   `XDG_STATE_HOME` holds three records, the unresolved one included, each
   failing or passing one with its whole output in a file, and nothing is
   written in the repository's working tree. Closed by: a fixture naming
   REQ-0146, seen failing first.
2. Given a passing run, when `evidence` runs, then it exits 0 with `current`;
   after a file changes, 1 with `stale`; after a failing run, 1; after a verb
   that rewrote a file, 1; after the file is put back to a tree that passed
   earlier with a later run between, 1; and for a verb never run, 3. Closed
   by: fixtures naming REQ-0146, seen failing first.
3. Given an untracked file, when `run` records a verb and every file is then
   committed, then the recorded tree id equals the commit's tree. Closed by: a
   fixture naming REQ-0146.
4. Given a directory that isn't a git work tree, when `run` and then
   `evidence` run, then the record's tree id is `none` and `evidence` exits 3.
   Closed by: a fixture naming REQ-0146.

## What to do

Add the ledger, the tree id and the `evidence` command to the native tool's
`verbs` feature, state them on `meow-verbs`' page, and move the unit to its
next minor version.

## Depends on

Nothing. ADR-1480 is approved.

## Evidence

Not yet.

## Left alone

The skill and the implement step, which TSK-2280 changes.
