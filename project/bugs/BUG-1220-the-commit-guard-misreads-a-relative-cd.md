---
id: BUG-1220
artifact: bug
status: approved
severity: minor
violates: REQ-1292
enters: implement
found: 2026-09-27
revised: 2026-09-27
issue: 567
---

# `meow-git`'s commit guard resolves a relative `cd` against the session's directory

## Reproduction

With `meow-git` 0.2.2 and Claude Code's Bash tool, in a session whose working
directory is the main checkout on `main`, on the trunk after #566:

1. Run one command that changes to a work tree on a branch, then runs a
   subshell that changes to `plugins/meow-verbs/tests` and runs the tests,
   then commits.
2. The guard refuses it.

```text
meow-git: refused a commit on `main`, the trunk this repository declares. Take a branch and commit there.
```

The same command with the subshell run separately commits on the branch.

## What the system does

The guard tracks the directory of the last `cd` before the commit, and
replaces it with each `cd` it meets. The relative `plugins/meow-verbs/tests`
replaces the absolute work tree, and the guard then resolves that relative
path against the session's directory, the main checkout, where the branch is
`main`.

## What it should do, and why

A relative `cd` moves from where the command already is, so it joins onto the
directory before it. REQ-1292 keeps commits off the trunk, and a guard that
refuses a commit made on a branch is a false positive, which the constitution
calls a defect in the check, because a guard that fires wrongly gets switched
off.

## Triage

A defect in the guard's reading of a command, so it enters at implementation
and needs no decision. Minor, because the refusal is safe and a retry with the
subshell split out works; the cost is a refused commit and a lost minute.

## Closed by

TSK-2390. The reproduction is now
`a_relative_cd_joins_the_directory_before_it` in `crates/meow/src/git.rs`,
which failed before the fix and passes after it, and stays as the regression
check.

## Tasks

- [x] T-001 TSK-2390 join a relative `cd` onto the directory before it, in
      `crates/meow/src/git.rs`
      evidence: the unit test, seen failing first, in #567.
