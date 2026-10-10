---
id: BUG-1530
artifact: bug
status: approved
severity: minor
violates: REQ-4300
enters: implement
found: 2026-10-10
revised: 2026-10-10
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The test stage takes five to sixteen minutes where five is the bound

`mise run test` runs the 14 unit suites, the crate's tests, the record check and
the scripts' tests in one `&&` chain, so it lasts as long as their sum.

## Reproduction

Seen on `main` at the commit of pull request 877, on Darwin arm64 with the
binaries built:

1. `plugins/meow-checks/bin/meow-checks run test`.
2. Read the line `passed, exit status 0 after <N>s` that the stage prints.

## What the system does

The stage took 962.5, 704.6, 354.3, 345.5, 330.7 and 319.6 seconds in six runs
(RES-0345). The suites' own lines sum to about 540 seconds, and the slowest,
`meow-flow`, takes 162 seconds.

## What it should do, and why

REQ-4300 asks for 300 seconds with the binaries built. A stage over that stops
being something a person waits for, and a run cut short by the limit of a tool
call reports nothing about the work.

## Triage

Enters at implement, because REQ-4300 states the bound and RES-0345 names where
the time goes. Minor, because the stage's result is right and only its duration
is wrong.

## Closed by

The reproduction's second step printing a duration under 300 seconds on the
owner's machine, recorded in the task's Evidence, and a check that counts the
suites the stage runs against the directories that hold tests, so a split
doesn't drop one.

## Tasks

- [x] T-001 TSK-5280 run the unit suites of the `test` stage at the same time, and keep the gate check reading it (done: pull request 879)
