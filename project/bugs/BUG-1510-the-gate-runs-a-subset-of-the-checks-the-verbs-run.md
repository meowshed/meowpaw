---
id: BUG-1510
artifact: bug
status: approved
severity: major
violates: REQ-1754
enters: implement
found: 2026-10-05
revised: 2026-10-05
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The gate runs a subset of the checks the verbs run

CI runs `mise run all`, whose `depends` lists fourteen tasks, while the
profile's verbs run far more: every unit's tests, the record's check, the
repository's own checks and two unit checks the `lint` verb names directly. A
contributor who runs the verbs reproduces failures CI never sees, the
opposite of REQ-1754, and three defects reached the trunk this way in one
week: the licensing gap BUG-1500, the broken `meow-gotask` test and the
stale versions in `docs/`.

## Reproduction

Seen on `main` at 466751bb, and at every revision since the profile's verbs
grew past the gate's list. From a checkout of `main`:

1. `meow-checks run lint` exits 1 with 100 licensing findings, where
   `mise run all` exits 0, because no task the gate runs carries the licence
   check (BUG-1500 holds the full reproduction).
2. `python3 -m unittest plugins.meow_gotask.tests.test_gotask` fails, where
   `mise run all` exits 0, because the gate runs no unit's tests at all.

## What the system does

The gate passes a commit whose verbs fail, so the trunk carries failures a
local run reports, and `mise run all` drifts further from the verbs each
time a check joins the profile without joining the gate.

## What it should do, and why

Every check the harness ships runs locally by the same command that runs it
in continuous integration (REQ-1754): the gate composes the verbs' members,
and a check joins the verbs and the gate together or not at all.

## Triage

It enters at `implement`, because REQ-1754 holds and what is missing is the
gate's coverage. Severity major: the gate is the mechanism that keeps the
trunk green (REQ-2210), and a gate that passes failing trees defeats it.

## Closed by

TSK-5230 moves the test chain into `[tasks.test]`, adds the two unit checks
the `lint` verb names, and extends `[tasks.all]`'s depends to every member
the verbs run, with `tools/check_gate_covers_verbs.py` holding the two
declarations together from then on.

## Tasks

- [x] T-001 TSK-5230 cover the verbs' members in the gate, and hold the two
      declarations together with a check
