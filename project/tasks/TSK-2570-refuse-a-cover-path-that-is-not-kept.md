---
id: TSK-2570
artifact: task
status: approved
revised: 2026-09-28
bug: BUG-1260
closes: []
issue: 643
---

# Refuse a Cover path that isn't a file kept in the repository

`paw ready implement` refuses a Cover whose `Checks` or `Failing run` names a
path that is absolute, leads outside the repository or isn't a regular file,
and one whose `Failing run` names a file `Checks` names. So the gate lets an
implementation start only once a run is kept in the repository beside its
checks. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given an approved open task whose Cover is otherwise filled, when
   `Failing run` names `/etc/hosts`, `../outside.txt` with that file present,
   or a directory in the repository, then `paw ready implement` exits 1 with
   a line naming that path. Closed by: the class `CoverPaths` in
   `plugins/meow-flow/tests/test_record.py`.
2. Given the same task, when `Checks` names an absolute path, a `..` escape or
   a directory, then `paw ready implement` exits 1 with a line naming that
   path. Closed by: the class `CoverPaths`.
3. Given the same task, when `Failing run` names the file `Checks` names, then
   `paw ready implement` exits 1 with a line naming that path as a check.
   Closed by: the class `CoverPaths`.
4. Given a Cover whose paths are relative regular files inside the repository,
   when `paw ready implement` runs, then it exits 0, as
   `Cover.test_implement_is_ready_once_the_cover_is_filled` already shows.
   Closed by: that fixture, unchanged.

## What to do

In `cover_gaps` in `crates/meow/src/record.rs`, test each path under `Checks`
and `Failing run` for being relative, for resolving inside the repository's
root once symbolic links and `..` are resolved, and for being a regular file,
and refuse a `Failing run` path that `Checks` also names. Each refusal names
the path on its own line. State the rule in SPC-1090's section "The gate".

`meow-flow` 0.34.0 isn't released yet, so the fix ships in it without a version
of its own. Write the checks first, in a commit of their own, and see them
fail.

## Depends on

Nothing. BUG-1260 is approved.

## Evidence

`cover_gaps` in `crates/meow/src/record.rs` asks a new function, `unkept`,
about each path under `Checks` and `Failing run`. It refuses an absolute path,
a path that resolves outside the repository's root once `..` and symbolic
links are resolved, and one that isn't a regular file. A `Failing run` path
that `Checks` also names is refused as a check. SPC-1090's section "The gate"
states the rule.

The four checks in the class `CoverPaths` failed first: `meow-verbs run test`
exited 1 with `FAILED (failures=4)`, seen in
the run under #647, whose output is no longer kept, in the commit that held the checks alone.
They pass now:

```text
$ python3 -m unittest test_record    # in plugins/meow-flow/tests
Ran 186 tests
OK                                   # exit 0
```

`meow-flow` 0.35.0 isn't released yet, so this fix ships in it without a
version of its own. `meow-verbs evidence --keep format lint check test build`
exits 0 on this change's own tree, each result kept in `project/evidence/`,
as the pull request cites.

## Left alone

Whether the kept run shows a failure, and whether it starts with the header
`meow-verbs evidence` writes: ADR-1620 leaves the first to the decision on
REQ-3206, and requiring the second would tie `meow-flow` to `meow-verbs`,
which REQ-0146 forbids.
