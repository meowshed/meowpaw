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

Not yet. The task closes on the fixtures passing, each shown first failing,
with the command, its exit status and its output.

## Left alone

The skill, the documentation page, the marketplace entry and this
repository's profile, which TSK-1290 adds.
