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

Not yet. The task closes on the fixtures passing, each shown first failing,
with the command, its exit status and its output.

## Left alone

The skill, the documentation page, the marketplace entry, this repository's
`[commits]` table and the temporary skill, which TSK-1310 handles.
