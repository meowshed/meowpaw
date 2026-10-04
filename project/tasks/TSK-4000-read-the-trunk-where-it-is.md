---
id: TSK-4000
artifact: task
status: done
revised: 2026-09-30
bug: BUG-1370
closes: []
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Read the trunk where it is

`paw` reads a task's approval on the trunk whatever the file's line endings
and whichever remote holds the trunk, says when it can't ask about one task,
and lists each trunk ref once in a run. One task, one branch, one pull
request, one review: the tests first, then the change, its documentation and
its marks.

## Acceptance criteria

1. Given a task approved on the trunk in a file with CRLF line endings, and
   the same task with LF endings on a branch, when `paw ready implement
<task>` runs on the branch, then it exits 0. Closed by: a fixture test in
   `plugins/meow-flow/tests/test_record.py`.
2. Given a trunk that exists only as the remote-tracking branch of a remote
   not named `origin`, when `paw ready implement` runs on a task absent from
   it, then it exits 1 naming the task and the trunk, and `paw status`
   prints no line saying the trunk names no branch. Closed by: a fixture
   test.
3. Given an open, approved task reached through a link that leaves the
   repository, when `paw status` runs, then it prints one line saying an
   approval can't be told from one waiting on a merge, naming the task, and
   `paw ready implement` still exits 0. Closed by: a fixture test.
4. Given a record with two open tasks under one epic and a trunk held by one
   ref, when `paw status` runs, then it starts `git ls-tree` once. Closed
   by: a fixture test that counts the calls through a `git` placed first on
   the path.
5. Given this change's tree, when `meow-checks run format lint check test`
   runs, then each passes. Closed by: each verb's outcome in the task's pull
   request.

Each criterion is decidable from this task's own work.

## What to do

Change `trunk_of` and `off_trunk` in `crates/meow/src/record.rs`. The remotes
read are the one the trunk's local branch tracks, `origin`, and the only
remote where there is one, because a task approved on any of them has been
merged. Two refs at one commit are read once. Keep the nineteen checks in
`OffTheTrunk` passing. Raise `meow-flow`'s patch version, and say in the
`meow-flow` page which remotes are read.

## Depends on

Nothing.

## Evidence

Five checks in `OffTheTrunk` in `plugins/meow-flow/tests/test_record.py`
close criteria 1 to 4: a trunk record with CRLF endings, a trunk on a remote
of another name, the remotes that aren't read, a task behind a link leaving
the repository, and one tree listing for each trunk commit. Four failed at
the pull request's first commit, and the fifth came with the code review's
fixes: two rounds of review found a fork's branch read as the trunk in four
cases, and a check that passed against a wrong implementation.
All pass at the last commit, with the checks that were there before. `meow-checks run format lint check test` passed all four
verbs. On this repository `paw status` started 22 git processes before the
change and 15 after it, with `ls-tree` down from 8 to 1.

## Left alone

`paw status` takes about 0.8 s on this repository before and after the
change. The git reads were never most of that: `paw count` and
`paw check relations` take 0.07 s, so the time is in what `status` computes
from the record, which no requirement bounds and ADR-2310's reversal line,
written about git reads, doesn't cover. A ref kept under `refs/remotes/`
for a remote other than `origin` that the repository doesn't configure isn't
read, so BUG-1370's
second case is closed for a configured remote alone, because such a ref may
be a fetched fork. CRLF endings are read only where the
trunk is asked about a task, so a record with CRLF endings in the working
tree still reads as it did.
