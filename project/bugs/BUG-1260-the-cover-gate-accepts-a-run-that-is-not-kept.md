---
id: BUG-1260
artifact: bug
status: approved
severity: major
violates: REQ-3207
enters: implement
found: 2026-09-28
revised: 2026-09-28
issue: 643
---

# `paw ready implement` accepts a Failing run that isn't a run kept in the repository

`paw ready implement` exits 0 on a Cover whose `Failing run` names a file
outside the repository, a directory, or the check file itself. So the
implementation starts although nothing was kept as the run in which the checks
failed, which is the evidence REQ-3207 asks the cover step to keep.

## Reproduction

`main` after #630, with `meow-flow` 0.35.0 built by `crates/meow/build-units`.

1. Take the fixture record in `plugins/meow-flow/tests/test_record.py`: an
   approved epic and an approved open task, TSK-0001, with the Cover the
   `Cover` fixtures call `FILLED`, and `tests/test_a_task.py` present.
2. Set its `Failing run` line to `/etc/hosts`, then to `../outside.txt` with
   that file present beside the repository, then to `tests`, then to
   `tests/test_a_task.py`.
3. Run `paw ready implement TSK-0001` after each.

## What the system does

Each of the four runs exits 0 and prints
`paw ready implement: ready; TSK-0001 approved and complete`. `Checks` accepts
the same kinds of path. The cause is `cover_gaps` in
`crates/meow/src/record.rs`, which asks only whether
`repository.join(path).exists()`: joining an absolute path returns that path,
a `..` component leaves the repository, and a directory exists.

## What it should do, and why

`ready implement` should exit 1, naming the path on its own line, where a path
under `Checks` or `Failing run` is absolute, leads outside the repository or
isn't a regular file, and where `Failing run` names a file `Checks` names.
REQ-3207 asks that the run in which the checks failed is kept as the cover
step's evidence, and a file outside the repository isn't kept with it, a
directory isn't a run, and the check isn't the run of the check.

Whether the kept run shows a failure stays outside this defect, because
ADR-1620 leaves it to the decision on REQ-3206. The gate still reads the four
lines and the files they name, and not their content.

## Triage

It enters at implement, because REQ-3207 is right and ADR-1620's rule that the
path under `Failing run` exists means a file kept in the repository, which the
program reads too loosely. Major, because the gate that holds REQ-3207 lets an
implementation start with no kept run, and nothing after it notices.

## Closed by

The reproduction as fixtures in the class `CoverPaths` in
`plugins/meow-flow/tests/test_record.py`: an absolute path, a `..` escape and
a directory, under `Failing run` and under `Checks`, and the check named as its
own failing run, each refused naming the path.

## Tasks

- [x] T-001 TSK-2570 refuse a Cover path that isn't a file kept in the
      repository, in `crates/meow/src/record.rs`
      evidence: 4 checks seen failing first, 186 `meow-flow` fixtures
      passing, in #647.
