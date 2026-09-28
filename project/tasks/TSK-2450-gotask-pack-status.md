---
id: TSK-2450
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1560
closes: [REQ-2480, REQ-2486, REQ-2508, REQ-2510]
issue:
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

Not yet.

## Left alone

`bind` and `check`, which TSK-2460 takes; REQ-2488, which ADR-1590 postpones.
