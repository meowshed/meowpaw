---
id: TSK-2270
artifact: task
status: done
revised: 2026-09-27
epic: EPC-1460
closes: [REQ-0146]
issue: 513
projected: 752962182cdf
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

Closes REQ-0146. `meow-verbs evidence format lint test` exits 0:

```text
format: passed, record e7091e682226, current at tree 8c370dc87ab6
lint: passed, record 43b24e86e05d, current at tree 8c370dc87ab6
test: passed, record 0c563b619de5, current at tree 8c370dc87ab6
```

Tree `8c370dc87ab6` is the working state before this section and the epic's
mark were written, so the committed tree differs from it by those two files,
which `git diff 8c370dc87ab6 HEAD` shows, because the recorded tree is a git
object. The `test` record covers the `meow-verbs` fixtures, 23 tests, OK. Each
criterion's check, each seen failing on the program before the change:

1. `Ledger.test_run_records_every_verb_outside_the_repository`.
2. `Ledger.test_evidence_holds_only_for_the_tree_it_ran_on`,
   `Ledger.test_a_verb_that_rewrites_the_tree_is_stale_until_it_runs_clean` and
   `Ledger.test_going_back_to_an_earlier_tree_is_stale_until_the_verb_runs_again`.
3. `Ledger.test_the_tree_id_is_the_tree_of_a_commit_adding_every_file`.
4. `Ledger.test_outside_git_a_record_is_bound_to_no_tree`.

Every fixture now sets its own `XDG_STATE_HOME`, so none writes to the
machine's ledger. The unit is at 0.4.0, the release ADR-1410 scheduled to stop
reading `fmt` and `typecheck`, so that reading is removed here and its two
fixtures now show the old names ignored and refused.

Writing evidence into the tree makes the tree it cites differ from the commit
by the evidence itself, which ADR-1480 didn't foresee. The difference is
readable with `git diff`, as above, and the verify step collects evidence
again on the merged tree.

## Left alone

The skill and the implement step, which TSK-2280 changes.
