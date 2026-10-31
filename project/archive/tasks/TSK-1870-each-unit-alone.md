---
id: TSK-1870
artifact: task
status: done
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

`tools/check_standalone.py` reads every file each unit ships, skipping its
measurement cases and fixtures, and reports a path through
`${CLAUDE_PLUGIN_ROOT}` or `${CLAUDE_SKILL_DIR}` that resolves outside the
unit, and a path into another unit's directory. It runs as the `standalone`
task in `mise run all`, which CI runs, and in the `lint` verb. Four fixtures:
paths inside a unit, and naming another unit in prose, pass; a climb out of a
unit and a path into another unit are each reported at their line; and a
fixture file naming another unit is skipped while a shipped one beside it is
reported. Against a check that finds nothing, all four fail.

`docs/README.md` gains "Adopt any part of it", stating that each unit is a
working harness alone and in any combination, and `CLAUDE.md`'s gate lists
the new check.

```text
$ python3 tools/check_standalone.py
84 unit files, 0 paths leaving their unit

$ python3 -m unittest tools/test_check_standalone.py
Ran 4 tests in 0.004s
OK
```

## Left alone

A doctor that reports every unit's capabilities at once, which ADR-1270
leaves.
