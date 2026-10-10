---
id: TSK-5280
artifact: task
status: approved
revised: 2026-10-10
bug: BUG-1530
closes: [REQ-4300]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Run the unit suites of the `test` stage at the same time

The `test` stage runs each unit's suite as a task of its own that the stage
depends on, so the suites run at the same time and the stage lasts as long as
the slowest, and the gate check keeps holding `[tasks.all]` to the stage.

## Acceptance criteria

1. Given the units' binaries built, when `meow-checks run test` runs on the
   owner's machine, then it passes and its reported duration is under 300
   seconds. Closed by: the line `passed, exit status 0 after <N>s` that the
   stage prints, recorded under Evidence.
2. Given the directories that hold tests under `plugins/` and `tools/`, when
   the stage's task graph is read, then every one of them is run by a task the
   stage depends on. Closed by: a test in `tools/` that fails where a
   directory with tests is run by no such task.
3. Given a profile whose `test` stage is a task with dependencies, when
   `tools/check_gate_covers_verbs.py` runs, then it reads the dependencies and
   reports a task that `[tasks.all]` doesn't carry. Closed by: a test in
   `tools/` with a fixture of one split stage and one uncovered task.

## What to do

Split `[tasks.test]` in `mise.toml` into one task for each directory that holds
a unit's tests, and make `test` depend on them, because mise runs a task's
dependencies at the same time. Keep the record check and the scripts' tests as
tasks the stage depends on as well. Teach `tools/check_gate_covers_verbs.py`
to follow `depends` as well as `&&`, as BUG-1510 asked of it. Don't change what
any suite checks, and don't delete a test to meet the bound.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

The build, which the `build` stage owns, a shared target directory across
worktrees, and the tests' own speed, which RES-0345 didn't profile.
