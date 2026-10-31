---
id: TSK-5160
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2605
closes: [REQ-2716, REQ-2727, REQ-2728]
issue: 1012
projected: dda1400fa66e
tracked: ec6ecb0ff572
---

# Hold the prose gate's network exception

Hold every hook to no network except the prose gate's bounded judge, and
advance the revision for failed tool attempts too.

## Acceptance criteria

1. Given ADR-2700's hook fixtures, only the bounded prose judge passes and
   every attempted tool use advances the revision. Closed by: author and hook
   fixtures for REQ-2716, REQ-2727 and REQ-2728.

## What to do

Implement the exception in `meow-author check` and the hook subcommands.

## Depends on

Nothing.

## Evidence

Most of ADR-2700 was already built when this task started: TSK-4900 named the
prose gate's judge as the one exception in `meow-author check`, and TSK-4910
advanced the revision counter after a failed tool use. The gap this task
closed is the bound. The check excused the gate's `claude -p` whatever the
hook's timeout, so a gate hook with no timeout passed, although ADR-2700
rests the exception on the 120-second bound ADR-2390 sets. The check now
excuses the judge only where the gate's hook declares a `timeout` above 0 and
at most 120 seconds, and otherwise fails it, naming the bound.

The criterion is closed by these tests, which together cover REQ-2716,
REQ-2727 and REQ-2728:

- `the_judge_is_excused_only_inside_its_bound`, in
  `crates/meow/tests/hook_rules.rs`, passes a gate hook whose timeout is 60 or
  120 and fails one whose timeout is 121, 0 or missing (REQ-2716, REQ-2727).
  It failed first, on 121, 0 and a missing timeout.
- In the same file, `a_hook_that_reaches_the_network_fails` fails a hook that
  calls `curl`, and `only_the_prose_gate_may_call_the_judge` fails `claude -p`
  in another unit and in another subcommand of the prose gate.
  `the_exception_excuses_the_judge_and_nothing_else` fails `curl` beside the
  judge, and `this_repositorys_units_pass` passes the shipped gate with its
  judge (REQ-2727).
- `a_failed_tool_use_advances_the_counter_and_so_does_a_successful_one`, in
  `crates/meow/tests/revision.rs`, and
  `Hooks.test_both_events_run_revision_on_the_four_tools`, in
  `plugins/meow-checks/tests/test_hooks.py`, hold every attempted use of the
  four tools that change the tree to one advance, a failed one included
  (REQ-2728).

`plugins/meow-author/README.md` and SPC-1240 state the bound.

The Pi package of `meow-checks` registers no hook, so a session on Pi
advances no revision counter. TSK-4910 left that gap, and this task, which
names `meow-author check` and the Claude Code hook subcommands, doesn't close
it.

Every stage passed in pull request #1072.

## Left alone

Non-hook commands.
