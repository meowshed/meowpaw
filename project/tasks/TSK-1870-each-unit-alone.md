---
id: TSK-1870
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1270
closes: [REQ-0012, REQ-0014, REQ-0034]
issue: 338
---

# Each unit stands alone, and a check holds it

Each unit stands alone, and a check holds it, as ADR-1270 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a unit file with a path climbing out of the unit or naming another unit's directory, when the check runs, then it reports the file and line. Closed by: a fixture.
2. Given this repository, when the check runs, then it reports nothing. Closed by: its output.

## What to do

Write `tools/check_standalone.py`, reporting a path in a unit's files that leaves the unit's directory and any reference to another unit's directory, with a fixture of its own, and run it in the `test` verb. State the adoption levels in `docs/README.md`: each unit alone, in any combination.

## Depends on

Nothing. ADR-1270 is approved.

## Evidence

Not yet.

## Left alone

A doctor that reports every unit's capabilities at once, which ADR-1270
leaves.
