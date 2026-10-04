---
id: TSK-2380
artifact: task
status: done
revised: 2026-09-27
epic: EPC-1530
closes: [REQ-0452, REQ-0454, REQ-0456]
issue: 563
projected: 368060c03da5
---

# A dirty submodule binds no result, and `evidence --kept` lists the evidence a change adds

The tree id is `none` where a submodule has uncommitted changes, and
`evidence --kept` lists each kept file the branch adds with its record, its
outcome and whether it matches `HEAD`. One task, one branch, one pull
request, one review.

## Acceptance criteria

1. Given the fixtures ADR-1560's first criterion lists, when they run, then
   each behaves as it says. Closed by: the trace and fixtures naming REQ-0452
   and REQ-0454, the new ones seen failing first.
2. Given the fixtures ADR-1560's second criterion lists, when they run, then
   each behaves as it says. Closed by: fixtures naming REQ-0456, seen failing
   first.

## What to do

Change the native tool's `verbs` feature and its fixtures, and state the
listing on `meow-verbs`' page, moving the unit to its next minor version.

## Depends on

Nothing. ADR-1560 is approved.

## Evidence

Closes REQ-0452, REQ-0454 and REQ-0456. `meow-verbs evidence --keep format
lint test` exits 0 on this change's own tree, each result kept in
`project/evidence/`, as the pull request cites.

The eight `Claims` fixtures failed on the program before the change, and the
`meow-verbs` suite now runs 59 tests, OK. Each criterion's check:

1. The existing `Ledger.test_run_records_every_verb_outside_the_repository`
   and `Ledger.test_evidence_holds_only_for_the_tree_it_ran_on` show a
   record's tree id and a stale record after a change, and
   `Claims.test_a_dirty_submodule_binds_no_result` and
   `Claims.test_an_edit_in_a_submodule_leaves_no_result_current` show the
   submodule gap closed, the second naming the submodule and exiting 3
   (REQ-0452, REQ-0454).
2. `Claims.test_the_listing_names_only_what_the_work_adds` lists only the
   branch's file with its record, differing before the commit and matching
   after; `test_a_superseded_file_is_listed_and_not_counted`,
   `test_a_failed_result_fails_the_listing`,
   `test_an_empty_listing_is_unresolved`,
   `test_with_no_trunk_every_file_is_listed_with_a_note` and
   `test_outside_git_each_file_is_bound_to_nothing` cover the rest (REQ-0456).

The first run of the verbs failed `test_a_superseded_file_is_listed_and_not_counted`:
two results kept within one second share a time, so which was latest was
decided by chance. The listing now breaks the tie by when each file was
written, and the fixture passed five runs of five. A fresh clone doesn't keep
file times, so two results kept within one second can still tie there; the
kept header's time is to the second, a limit ADR-1560 didn't foresee. That
failed run's kept file was deleted, not committed.

`meow-verbs` moves to 0.7.0.

## Left alone

Matching record identifiers in tasks, which ADR-1560 leaves to `paw`.
