---
id: TSK-2400
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1540
closes: [REQ-2522, REQ-2524, REQ-2540]
issue:
---

# The native tool reads paths with `-z`, reads git only through the lock-free helper, and writes no global configuration

What ADR-1570 decides for this part. One task, one branch, one pull request,
one review.

## Acceptance criteria

1. Given a file whose name holds a newline, a quote and a non-ASCII
   character, when the record check lists documents and the evidence listing
   lists kept files, then each reads the name as it is. Closed by: fixtures
   naming REQ-2522, seen failing first.
2. Given the reading helper, when a unit test inspects it, then it sets
   `GIT_OPTIONAL_LOCKS=0`; and a unit test fails where a source starts git
   outside the helper. Closed by: unit tests naming REQ-2524.
3. Given the native tool's sources, the shipped prompts under `plugins/` and
   the workflows under `.github/`, when a unit test scans them, then it fails
   on any naming `git config` with `--global` or `--system`, and passes on
   this repository. Closed by: a unit test naming REQ-2540, seen failing on a
   planted line.

## What to do

Change `crates/meow/src/record.rs` and `crates/meow/src/verbs/ledger.rs` to read with `-z`, add the unit tests to the crate, and move the units whose binary changes to their next patch version.

## Depends on

Nothing. ADR-1570 is approved.

## Evidence

Not yet.

## Left alone

REQ-2532 and REQ-2544, which ADR-1570 postpones.
