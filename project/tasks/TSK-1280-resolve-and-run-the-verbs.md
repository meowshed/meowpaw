---
id: TSK-1280
artifact: task
status: approved
revised: 2026-09-24
epic: EPC-1040
closes:
  [
    REQ-0130,
    REQ-0131,
    REQ-0134,
    REQ-0135,
    REQ-0136,
    REQ-0144,
    REQ-0150,
    REQ-0154,
    REQ-0156,
  ]
issue: 110
---

# Resolve and run the five verbs from the profile

One task, one branch, one pull request, one review.

## What to do

Create `plugins/meow-verbs/` with its manifest and licence headers. Write the
program SPC-1040 states: a launcher at `bin/meow-verbs` that finds Python 3.11
or later and reports every verb as "no interpreter" where it can't, and the
program it starts, with `status`, `status --json` and `run <verb>...`.

Resolve a verb only from `[verbs]` in `.meowpaw/profile.toml` at the
repository's root (REQ-0134). Report the five kinds of unresolved SPC-1040
names (REQ-0154), list keys the unit ignores, and run nothing from `status`
(REQ-0150). From `run`, record each verb's exact command, exit status,
duration and whole output, lead a failed verb with its last lines (REQ-0135,
REQ-0144, REQ-0156), and exit 0 only when every named verb passed (REQ-0136).

Write a fixture for every row of SPC-1040's failure paths and for each of
ADR-1070's first five checks, each seen failing first against a program that
returns nothing (REQ-2072). The fixtures run under this repository's `test`
verb once TSK-1290 declares it, and by hand until then.

## Depends on

Nothing. ADR-1070 and SPC-1040 are approved.

## Evidence

`plugins/meow-verbs/` carries the manifest, a budget of 0 characters, the
launcher `bin/meow-verbs`, the program `lib/meow_verbs.py` and twelve fixtures
in `tests/test_verbs.py`: one for each row of SPC-1040's failure paths, one for
each of ADR-1070's first five checks, and one refusing a sixth verb (REQ-0131).
Each builds a repository in a temporary directory and runs the launcher there.

Each fixture was first seen failing against a launcher that returns nothing,
then passing against the program:

```text
$ MEOW_VERBS_BIN=stub/meow-verbs python3 -m unittest discover -s plugins/meow-verbs/tests
Ran 12 tests in 0.087s
FAILED (failures=6, errors=6)
exit 1

$ python3 -m unittest discover -s plugins/meow-verbs/tests
Ran 12 tests in 0.716s
OK
exit 0
```

The budget was TSK-1290's to add, and it lands here, because the gate's budget
check fails a unit that states none. It stands at 0 until the skill arrives.
REQ-0130, REQ-0131, REQ-0134, REQ-0135, REQ-0136, REQ-0144, REQ-0150,
REQ-0154 and REQ-0156 are closed.

## Left alone

The skill, the documentation page, the marketplace entry and this
repository's profile, which TSK-1290 adds.
