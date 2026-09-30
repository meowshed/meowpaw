---
id: TSK-3340
artifact: task
status: approved
revised: 2026-09-29
bug: BUG-1342
closes: []
issue: 692
---

# Make the `meow-unattended` checks fail on a plan that ignores the declaration

The checks in `plugins/meow-unattended/tests/test_unattended.py` declare
values other than the defaults the fixtures shared, read the snapshot's
table, and match the command line and the stated limits exactly, so each of
the nine mutants BUG-1342 names fails at least one of them. One task, one
branch, one pull request, one review.

## Acceptance criteria

1. Given each of the nine mutants BUG-1342 names, built alone, when the unit
   suite runs against it through `MEOW_UNATTENDED_BIN`, then it exits 1.
   Closed by: the mutant run recorded under Evidence, and the kept run of
   the eight compatible mutants built together.
2. Given the shipped `meow-unattended`, when the unit suite runs, then it
   exits 0. Closed by: `python3 -m unittest test_unattended` in
   `plugins/meow-unattended/tests`.
3. Given this change's tree, when `meow-verbs run format lint check test
build` runs, then each passes. Closed by: the kept evidence of that run.

## What to do

In `plugins/meow-unattended/tests/test_unattended.py`:

- run `test_command_line_states_the_posture` for each of the five modes, and
  need the declared mode after `--permission-mode` and in the snapshot;
- count each flag, `-p` and `--verbose` among them, exactly once within
  `command_line(output)`;
- compare the snapshot's `meowpaw.unattended` with the declared table,
  `gates` included;
- add `permission_mode = "yolo"` to `test_refused_values`;
- declare `trunk = "trunk-x"` in `test_push_rules`, and need exactly its
  three push rules and no rule naming `main`;
- declare `root = "records"` in `test_approved_records_are_denied`, with an
  approved epic and research file that are not denied and approved files
  under `project/` that aren't the record;
- match each limit by the sentence that carries it.

The shipped program doesn't change, so no unit version is raised.

## Depends on

Nothing. BUG-1342 is approved, and TSK-3330 has landed.

## Evidence

The checks now run the posture test for each of the five modes and compare
the snapshot's `meowpaw.unattended` with the declared table. They count each
flag exactly once within the printed command, refuse `yolo` as a mode, and
declare `trunk = "trunk-x"` and `root = "records"`. The record fixture holds
an approved epic and research file, with approved files under `project/`
outside the record. Each limit is matched by its whole sentence.

Criterion 1. Before the change, each mutant BUG-1342 names, built alone with
`cargo build --release --features unattended` from a scratch copy of
`crates/meow` and run through `MEOW_UNATTENDED_BIN`, passed the old suite with
exit 0 and `OK`. Against the new suite each exits 1:

| Mutant | Exit | Result                | Check that fails it                         |
| ------ | ---- | --------------------- | ------------------------------------------- |
| A      | 1    | `FAILED (failures=5)` | `Plan.test_command_line_states_the_posture` |
| B      | 1    | `FAILED (failures=1)` | `Snapshot.test_push_rules`                  |
| C      | 1    | `FAILED (failures=1)` | `Snapshot.test_approved_records_are_denied` |
| D      | 1    | `FAILED (failures=5)` | `Plan.test_command_line_states_the_posture` |
| E      | 1    | `FAILED (failures=1)` | `Snapshot.test_approved_records_are_denied` |
| F      | 1    | `FAILED (failures=6)` | `Plan.test_command_line_states_the_posture` |
| G      | 1    | `FAILED (failures=6)` | `Plan.test_command_line_states_the_posture` |
| H      | 1    | `FAILED (failures=2)` | `Refusals.test_refused_values`              |
| I      | 1    | `FAILED (failures=2)` | `Plan.test_output_states_the_limits`        |

The failing run, under #694, whose output is no longer kept, is
`meow-verbs run test` with `MEOW_UNATTENDED_BIN` naming one binary that
holds every mutant but D, which edits the same line as H. It exited 1 with
`FAILED (failures=12)` across the posture, limits, push-rule, record and
refusal checks. The kept file doesn't record `MEOW_UNATTENDED_BIN`, so this
paragraph is what says the run tested a mutant.

Criterion 2:

```text
$ python3 -m unittest test_unattended    # in plugins/meow-unattended/tests
Ran 19 tests
OK                                       # exit 0
```

Criterion 3: `meow-verbs run format lint check test build` passes on this
change's tree, and `meow-verbs evidence --keep` keeps each result in
`project/evidence/`, as the pull request cites.

## Left alone

A mutation tool bound as a verb, which no pack names for this repository; the
nine mutants are the ones BUG-1342 reports. The checks for REQ-2392, which
TSK-3330 already tightened.
