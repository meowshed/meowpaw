---
id: TSK-2400
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1540
closes: [REQ-2522, REQ-2524, REQ-2540]
issue: 571
projected: 207489a53595
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

Closes REQ-2522, REQ-2524 and REQ-2540. `meow-verbs evidence --keep format
lint test` exits 0 on this change's own tree, each result kept in
`project/evidence/`, as the pull request cites. Each criterion's check:

1. `record::tests::a_document_with_an_unusual_name_is_listed_as_it_is` failed
   before the change and passes after it, and
   `Kept.test_an_unusual_evidence_path_is_read_as_it_is` failed on `main`'s
   program and passes on this one (REQ-2522). `check-ignore` takes `-z` only
   with `--stdin`, so the kept file's path now goes to it on standard input.
2. `profile::tests::a_read_takes_no_optional_lock` and
   `profile::tests::git_starts_only_in_the_reading_helper` pass; both hold what
   was already so (REQ-2524).
3. `profile::tests::nothing_the_harness_ships_writes_global_git_configuration`
   failed on a planted line under `plugins/` naming the global flag, and passes
   without it, having scanned more than twenty files (REQ-2540).

`meow-flow` moves to 0.33.3 and `meow-verbs` to 0.7.1.

## Left alone

REQ-2532 and REQ-2544, which ADR-1570 postpones.
