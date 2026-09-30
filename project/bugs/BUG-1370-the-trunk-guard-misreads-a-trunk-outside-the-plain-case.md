---
id: BUG-1370
artifact: bug
status: approved
severity: minor
violates: [REQ-3662, REQ-3664]
enters: implement
found: 2026-09-30
revised: 2026-09-30
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The trunk guard misreads a trunk outside the plain case

`paw ready implement` and `paw status` judge a task's approval on the declared
trunk wrongly in three cases: a trunk record with CRLF line endings, a trunk
held on a remote not named `origin`, and a task reached through a link that
leaves the repository. `paw status` also starts two git processes for every
ref each time it asks about a task, and asks twice about some.

## Reproduction

`meow-flow` 0.46.0 at the commit of #768 on `main`, git 2.55.0 on macOS, on
2026-09-30. Each case starts from a fresh repository holding a copy of this
repository's `project/`, a profile declaring `[git] trunk = "trunk0"`, and one
commit on `trunk0`. TSK-3350 is approved and open in that record.

1. Rewrite TSK-3350's file with CRLF line endings, commit it on `trunk0`,
   create a branch `work`, restore the file's LF form there, and run
   `paw ready implement TSK-3350`.
2. Create a branch `work`, point `refs/remotes/upstream/trunk0` at the first
   commit, delete the local `trunk0`, and run `paw status`.
3. Move `project/tasks` outside the repository, leave a symbolic link to it
   in its place, and run `paw ready implement TSK-3350` and `paw status`.
4. In this repository, run `time paw status`.

## What the system does

1. It exits 1 with "TSK-3350 is not approved on trunk0 yet", though the task
   is approved on the trunk.
2. It prints "the declared trunk trunk0 names no branch", though the remote
   `upstream` holds that branch.
3. `ready` exits 0, and `status` names the task next and prints no line
   saying an approval can't be told from one waiting on a merge.
4. It takes 0.78 s, against the second at which ADR-2310 says the decision
   would be reversed.

## What it should do, and why

A task approved on the trunk isn't waiting on a merge, so case 1 exits 0: the
status REQ-3662 reports is for a record absent from the trunk. In case 2 the
program reads the trunk on the remote that holds it, because REQ-3664's line
is for a trunk that can't be read, and this one can. In case 3 the trunk
can't say anything about the task, so `status` prints that line, naming the
task, as REQ-3664 asks. In case 4 the git reads stay well under the second,
so a record that grows doesn't reverse the decision.

## Triage

It enters at implement, because the requirements are right and the program
misses them. Minor, because each case needs an unusual repository, the
second and third fail open, and the first is cleared by rewriting the file on
the trunk. TSK-3880's `## Left alone` names the first two.

## Closed by

Not closed.

## Tasks

- [ ] T-001 TSK-4000 read the trunk where it is, in
      `crates/meow/src/record.rs`
