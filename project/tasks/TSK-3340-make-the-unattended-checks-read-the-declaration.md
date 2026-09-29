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

## Cover

- Checks: plugins/meow-unattended/tests/test_unattended.py
- Failing run: project/evidence/c763123d81b8.txt
- Landed in: not yet
- Judgement: 1: a mutant is a program nobody ships, so the failing runs
  come from binaries built outside the tree, and review reads each mutation
  in BUG-1342's table and the result for each in Evidence; 3: the kept run of the five verbs at the
  revision that merges closes it, and no check written before the work can

## Evidence

Not yet.

## Left alone

A mutation tool bound as a verb, which no pack names for this repository; the
nine mutants are the ones BUG-1342 reports. The checks for REQ-2392, which
TSK-3330 already tightened.
