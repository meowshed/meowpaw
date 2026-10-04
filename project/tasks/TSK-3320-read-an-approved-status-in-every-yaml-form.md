---
id: TSK-3320
artifact: task
status: done
revised: 2026-09-29
bug: BUG-1340
closes: []
issue: 674
---

# Read an approved record's status in every form `paw check` reads

`meow-unattended plan` denies `Edit` on an approved requirement or decision
whether its `status` is quoted, carries a trailing comment, or sits in a file
with CRLF line endings, so no approved record goes unprotected because of how
its YAML is written. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given approved requirements written `status: approved`,
   `status: "approved"`, `status: approved # frozen`, and `status: approved`
   with CRLF line endings, and a draft written `status: "draft"`, when `plan`
   runs, then the snapshot holds exactly four deny rules on the record, one
   for each approved file. Closed by:
   `Snapshot.test_approved_in_every_front_matter_form` in
   `plugins/meow-unattended/tests/test_unattended.py`.
2. Given this change's tree, when `meow-verbs run format lint check test
build` runs, then each passes. Closed by: the kept evidence of that run.

## What to do

In `crates/meow/src/unattended.rs`, read front matter with CRLF line endings,
and compare `artifact` and `status` with a trailing comment and the
quotes removed, as `bare` in `crates/meow/src/record.rs` does, so the two
readers of the record agree on which files are approved. Raise
`meow-unattended` to 0.2.1 in `plugin.json`, and its README's `describes:`
with it, because a fix changes what the unit ships.

Write the check first, in a commit of its own, and see it fail.

## Depends on

Nothing. BUG-1340 is approved.

## Evidence

`approved` in `crates/meow/src/unattended.rs` now compares `artifact` and
`status` through `bare`, which drops a trailing comment and the quotes as
`bare` in `crates/meow/src/record.rs` does, and `front_matter` reads CRLF line
endings as LF. SPC-1200's section "The snapshot" states both. `meow-unattended`
is 0.2.1.

The check failed first: `meow-verbs run test` exited 1 with
`FAILED (failures=1)` on `Snapshot.test_approved_in_every_front_matter_form`,
seen in the run under #675, whose output is no longer kept, in the commit that held the check
alone. It passes now, unchanged:

```text
$ python3 -m unittest test_unattended    # in plugins/meow-unattended/tests
Ran 18 tests
OK                                       # exit 0
```

Criterion 2: `meow-verbs run format lint check test build` passes on this
change's tree, and `meow-verbs evidence --keep` keeps each result in
`project/evidence/`, as the pull request cites.

## Left alone

A full YAML parser, which the `unattended` feature doesn't carry and the two
readers would then disagree on again. A block scalar or a flow mapping as a
`status` value, which no record kind uses.
