---
id: TSK-1300
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1050
closes:
  [
    REQ-1290,
    REQ-1294,
    REQ-1295,
    REQ-1302,
    REQ-1308,
    REQ-1310,
    REQ-1314,
    REQ-1318,
  ]
issue: 126
---

# Check a commit message against the declared convention

One task, one branch, one pull request, one review.

## What to do

Create `plugins/meow-scm/` with its manifest, its licence headers and a
budget of 0 until the skill arrives. Write the program SPC-1050 states: a
launcher at `bin/meow-scm` that finds Python 3.11 or later and reports a
message as unchecked where it can't, and the program it starts, with
`convention` and `check-message`.

Read `[commits]` from `.meowpaw/profile.toml` at the repository's root
(REQ-1290, REQ-1302, REQ-1308, REQ-1318), and report ignored keys. Check the
message for every row of SPC-1050's table, naming the rule and the line, and
apply the attribution check whatever the profile declares (REQ-1294, REQ-1295,
REQ-1310). Exit 0, 1 or 3 as SPC-1050 states (REQ-1314).

Write a fixture for every row of the check table and of the failure paths,
and for each of ADR-1080's first four checks, each seen failing first against
a program that returns nothing (REQ-2072). Run the check over this
repository's last ten commits on `main` for criterion 5, once TSK-1310
declares the convention.

## Depends on

Nothing. ADR-1080 and SPC-1050 are approved.

## Evidence

`plugins/meow-scm/` carries the manifest, a budget of 0 characters, the
launcher `bin/meow-scm`, the program `lib/meow_scm.py` and fourteen fixtures in
`tests/test_scm.py`: one for each row of SPC-1050's check table and failure
paths, and one for each of ADR-1080's first four checks, including a path and
a product name that the attribution check must not trip on. The fixture file
builds its attribution samples from parts, so the file itself carries none.

Each fixture was first seen failing against a launcher that returns nothing,
then passing against the program. The first run against the stub found two
fixtures that passed on the exit status alone; each now also asserts the
line the program prints:

```text
$ MEOW_SCM_BIN=stub/meow-scm python3 -m unittest discover -s plugins/meow-scm/tests
FAILED (failures=14)
exit 1

$ python3 -m unittest discover -s plugins/meow-scm/tests
Ran 14 tests in 0.663s
OK
exit 0
```

REQ-1290, REQ-1294, REQ-1295, REQ-1302, REQ-1308, REQ-1310, REQ-1314 and
REQ-1318 are closed.

## Left alone

The skill, the documentation page, the marketplace entry, this repository's
`[commits]` table and the temporary skill, which TSK-1310 handles.
