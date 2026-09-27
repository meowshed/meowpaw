---
id: TSK-2350
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1510
closes:
  [
    REQ-0752,
    REQ-0754,
    REQ-0756,
    REQ-0758,
    REQ-2958,
    REQ-2960,
    REQ-2962,
    REQ-2966,
    REQ-2967,
    REQ-2970,
  ]
issue: 548
projected: e38477c34117
---

# The ledger holds to the state rules

What ADR-1530 decides for this part, in the native tool's `verbs` feature, with its fixtures. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the fixtures ADR-1530's second criterion lists for identity, absent lines, the lock, pruning, purging, the environment switches, `state` and `evidence --all`, when they run, then each behaves as that criterion says. Closed by: fixtures naming each requirement, seen failing first.

## What to do

Change the native tool's `verbs` feature and its fixtures, state the change on `meow-verbs`' page, and move the unit to its next minor version where it hasn't moved since the last release.

## Depends on

TSK-2340, whose kept files the pruning leaves alone.

## Evidence

Closes REQ-0752, REQ-0754, REQ-0756, REQ-0758, REQ-2958, REQ-2960, REQ-2962,
REQ-2966, REQ-2967 and REQ-2970. `meow-verbs evidence format lint test` exits
0 on this change's own tree, each result kept in `project/evidence/`, as the
pull request cites.

The ten `State` fixtures failed on the program before the change, nine
failures and one error, and the `meow-verbs` suite now runs 48 tests, OK:

- `test_each_record_names_the_repository_and_work_tree` (REQ-0752);
- `test_a_corrupt_line_reads_as_absent` (REQ-0754);
- `test_state_prints_the_ledger_facts` (REQ-0756);
- `test_a_fresh_lock_holds_the_prune_and_the_append_waits`, which starts a
  run while a fresh lock is held, sees it wait, releases the lock and finds
  both its record and the old one kept (REQ-0758, REQ-2958, REQ-2967);
- `test_a_stale_lock_is_replaced` (REQ-2967);
- `test_state_off_writes_nothing_outside_the_repository` and
  `test_the_state_directory_moves` (REQ-2960);
- `test_old_records_and_their_output_are_pruned`, which also finds no
  `.partial` file left, and `test_purge_empties_the_ledger` (REQ-2962,
  REQ-2966);
- `test_all_adds_the_other_work_trees` (REQ-2970).

## Left alone

The other tasks of EPC-1510.
