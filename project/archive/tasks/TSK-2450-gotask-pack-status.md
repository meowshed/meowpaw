---
id: TSK-2450
artifact: task
status: done
revised: 2026-09-27
epic: EPC-1560
closes: [REQ-2480, REQ-2486, REQ-2508, REQ-2510]
issue: 589
projected: 2f02c2be4f32
---

# Ship the go-task pack with `status`

`meow-gotask status` detects Task, names each remote include before listing,
lists the tasks with `TASK_TEMP_DIR` outside the repository, and reports each
task's origin, blocks and freshness and each secret variable, as SPC-1150
states. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given a Taskfile with a plain task, an internal one, a prompting one, one
   requiring a variable, one ignoring errors on a command, one depending on it, one with `if`, one
   with `platforms`, one with `status`,
   one with `sources` and `method: timestamp`, and a local include, when
   `status` runs, then each carries its block or freshness line and the
   included task its namespace. Closed by: fixtures naming REQ-2480 and
   REQ-2508, seen failing first.
2. Given a task with `sources`, when `status` runs and then `task` runs that
   task, then the task runs, and the work tree reads as before. Closed by: a
   fixture.
3. Given a remote include, when `status` runs, then the include is named,
   the result is `unresolved: remote include` with exit 3, and no Task ran.
   Closed by: a fixture naming REQ-2486.
4. Given a `secret: true` variable, when `status` runs, then it is named as
   masked and not protected, and its value is absent. Closed by: a fixture
   naming REQ-2510.
5. Given a stand-in Task exiting 104, 106, or 2 with `unknown flag`, when
   `status` runs, then each is unresolved with exit 3, and 104 never reads as
   untrusted. Closed by: fixtures.

## What to do

Move the code `meow-mise` and this pack share into one module both features
compile, add a `gotask` feature with a YAML parser behind it, and add the unit
under `plugins/meow-gotask` with its launcher, skill, README, budget,
requirement file and marketplace entry, built by `build-units` and tested by
the `test` verb. `meow-mise`'s 38 fixtures keep passing.

## Depends on

Nothing. ADR-1590 is approved.

## Evidence

Closes REQ-2480, REQ-2486, REQ-2508 and REQ-2510. The 22 fixtures in
`plugins/meow-gotask/tests/test_gotask.py` all failed first against a program
that reports nothing. One of them failed first for a fault in the fixture, a
task already fresh before any listing, and now uses a checksum task. It fails
against a program that lists without moving `TASK_TEMP_DIR` and passes
against the unit. All 22 pass against real Task 3.53.1. `meow-mise`'s 38
fixtures pass unchanged against the shared `runner` module. `meow-verbs
evidence --keep format lint test` exits 0 on this change's own tree, each
result kept in `project/evidence/`, as the pull request cites.

## Left alone

`bind` and `check`, which TSK-2460 takes; REQ-2488, which ADR-1590 postpones.
