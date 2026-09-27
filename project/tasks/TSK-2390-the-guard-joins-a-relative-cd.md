---
id: TSK-2390
artifact: task
status: approved
revised: 2026-09-27
bug: BUG-1220
closes: [REQ-1292]
issue: 567
---

# `meow-git`'s commit guard joins a relative `cd` onto the directory before it

The guard's scan of a command joins a relative `cd` onto the directory the
last `cd` named, so a subshell's `cd` inside a work tree stays in that work
tree. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given a command that changes to a work tree on a branch, then to a relative
   directory in a subshell, then commits, when the guard reads it, then it
   lets the commit through; given the same with the work tree on the trunk,
   it refuses. Closed by: a unit test naming REQ-1292, seen failing first.

## What to do

Change `invocation` in `crates/meow/src/git.rs` to join a relative `cd` onto
the directory before it, with a unit test, and move `meow-git` to its next
patch version.

## Depends on

Nothing. BUG-1220 is approved.

## Evidence

Closes REQ-1292. `meow-verbs evidence --keep format lint test` exits 0 on this
change's own tree, each result kept in `project/evidence/`, as the pull
request cites.

`a_relative_cd_joins_the_directory_before_it` in `crates/meow/src/git.rs`
failed before the change and passes after it, beside
`an_absolute_cd_replaces_the_directory`; the crate's `git` tests run 5, OK,
and the `meow-git` fixtures pass. The tests spell the commit command in parts,
because the guard reads the text of any shell command that names one, this
file's included. `meow-git` moves to 0.2.3.

## Left alone

The rest of the guard's reading.
