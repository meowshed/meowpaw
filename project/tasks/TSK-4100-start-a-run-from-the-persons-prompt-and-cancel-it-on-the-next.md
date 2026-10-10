---
id: TSK-4100
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2300
closes:
  [
    REQ-0872,
    REQ-0874,
    REQ-0890,
    REQ-0894,
    REQ-2660,
    REQ-2962,
    REQ-3700,
    REQ-3712,
  ]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Start a run from the person's prompt, and cancel it on the next one

`/meow-loop:run` starts a run inside the session, the `UserPromptSubmit` hook
writes its state and cancels it on any later prompt, and the `PreToolUse`
guard keeps the run's state and the `meow-loop` command out of the model's
reach, as SPC-1201 states under "Starting a run", "A run's files",
"Cancelling" and "The guards". One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a fixture work tree and a `UserPromptSubmit` input whose prompt is
   `/meow-loop:run --iterations 3 --hours 1 --tokens 100000`, when
   `meow-loop prompt` runs, then a run directory holds `run.toml` with the
   session id and the three bounds, and an empty `progress/progress.md`
   (REQ-3700, REQ-0872). Closed by: a fixture naming REQ-3700, seen failing
   first.
2. Given the start command with a bound missing or not a number above 0, when
   `meow-loop prompt` runs, then it writes no run directory and its
   `systemMessage` names each bound (REQ-0872). Closed by: a fixture naming
   REQ-0872.
3. Given an active run, when the next prompt is anything but the start
   command, then `run.toml` records `cancelled` with `cancelled_by = "person"`
   and the time, and the prompt goes through (REQ-3712, REQ-0890). Closed by: a
   fixture naming REQ-3712.
4. Given an active run, when `meow-loop guard` receives an Edit of `run.toml`
   or a Bash command `meow-loop stop`, then it denies both, and it allows an
   Edit of `progress/progress.md` and `report.md` (REQ-0874, REQ-2660). Closed
   by: a fixture naming REQ-2660.
5. Given the skill file `plugins/meow-loop/skills/run/SKILL.md`, when a
   fixture reads its front matter, then it sets
   `disable-model-invocation: true` (REQ-0894). Closed by: a fixture naming
   REQ-0894.
6. Given 21 run directories in one work tree, when a run starts, then 20
   remain, and `meow-loop purge` removes them all (REQ-2962). Closed by: a
   fixture naming REQ-2962.
7. Given `meow-loop start` from a terminal, when it runs, then its first line
   is the deprecation line SPC-1201 gives. Closed by: a fixture.

## What to do

Add the `run` skill, the `prompt` subcommand and its hook entry, and extend
`guard` for an active run. The hook reads the session id and the prompt from
its JSON input. Keep `start` working, with the deprecation line first. The
unit's README states the new start command. Bump `meow-loop` as a `feat`.

## Depends on

Nothing.

## Evidence

Pull request 881. The tests are in `plugins/meow-loop/tests/test_session_run.py`:

- Criterion 1: `Starting.test_the_start_command_writes_a_run_with_its_bounds`.
- Criterion 2: `Starting.test_a_missing_or_bad_bound_writes_nothing_and_names_each`.
- Criterion 3: `Cancelling.test_the_next_prompt_cancels_an_active_run`.
- Criterion 4:
  `Guarding.test_the_guard_denies_the_runs_terms_and_its_own_command_and_allows_its_notes`.
- Criterion 5: `Skill.test_the_start_command_cannot_be_invoked_by_the_model`.
- Criterion 6:
  `Starting.test_twenty_one_runs_leave_twenty_and_purge_removes_them_all`.
- Criterion 7: `Deprecated.test_the_terminal_runner_says_it_is_deprecated_first`.

The old suite `test_loop.py` passes against the shared binary (103 tests). It
needed the launcher to name the unit's directory (`MEOW_LOOP_UNIT`) and its
layout (`MEOW_LAYOUT`), because the shared binary sits in the core unit, and a
commit of its own for each carries the test that failed first.

## Left alone

The `Stop` hook and the endings other than `cancelled`, which TSK-4110 adds.
The posture check at start, which TSK-4120 adds.
