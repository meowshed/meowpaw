---
id: BUG-1342
artifact: bug
status: approved
severity: major
violates: REQ-2388
enters: cover
found: 2026-09-29
revised: 2026-09-29
issue: 692
---

# The `meow-unattended` suite passes a plan that ignores the declared posture

`plugins/meow-unattended/tests/test_unattended.py` passes against versions of
`meow-unattended plan` that ignore what the repository declares, so the
checks that close REQ-2388 can't tell a correct plan from one that breaks it.
The shipped program passes the suite and I found no defect in it; the defect
is in the checks.

## Reproduction

`main` after #683, with `meow-unattended` 0.2.2. Build `crates/meow` with the
`unattended` feature once for each mutation below, each applied alone to
`crates/meow/src/unattended.rs`. Point `MEOW_UNATTENDED_BIN` at a launcher that
runs the mutant binary with `unattended`, and run
`python3 -m unittest test_unattended` in `plugins/meow-unattended/tests`.

| Mutant | What the mutant does                                               |
| ------ | ------------------------------------------------------------------ |
| A      | prints `--permission-mode dontAsk` whatever the table declares     |
| B      | writes the push rule for `main` whatever `[git] trunk` declares    |
| C      | reads the record under `project` whatever `[record] root` declares |
| D      | refuses every mode but `dontAsk`                                   |
| E      | denies every approved record file, whatever its kind               |
| F      | leaves `gates` out of the snapshot                                 |
| G      | prints `--verbose` on a line of its own, outside the command       |
| H      | accepts any mode but `bypassPermissions`                           |
| I      | prints that a merge through the code host's interface is denied    |

## What the system does

Each of the nine mutants passes all 19 checks, exit 0 and `OK`. Every fixture
declares `dontAsk`, `trunk = "main"` and `root = "project"`, and the record
fixture holds only requirements and decisions. No check reads the snapshot's
`meowpaw.unattended` table. `test_command_line_states_the_posture` counts the
flags over the whole output and not within the command, and
`test_output_states_the_limits` matches fragments such as `code host`, which
an inverted limit still holds.

## What it should do, and why

Each mutant fails at least one check, because REQ-2388 says the run's posture
comes from what the repository declares, and a suite that passes a plan
ignoring the declaration is no evidence that `plan` meets it. EPC-1900's
criteria 2, 5 and 6 name the declared mode, the declared trunk and the
approved requirements and decisions, and SPC-1200 says the snapshot holds the
resolved table; the checks have to fail when any of those is ignored.

## Triage

It enters at cover, because REQ-2388, ADR-2000, SPC-1200 and the program are
right and the task's checks miss what the requirement asks. Major, because
REQ-2388 is recorded as closed on evidence that would stay green if the
program regressed.

## Closed by

The nine mutants, each failing the strengthened suite, as TSK-3340's evidence
records. The checks live in
`plugins/meow-unattended/tests/test_unattended.py`.

## Tasks

- [ ] T-001 TSK-3340 make the `meow-unattended` checks fail on a plan that
      ignores the declaration, in
      `plugins/meow-unattended/tests/test_unattended.py`
