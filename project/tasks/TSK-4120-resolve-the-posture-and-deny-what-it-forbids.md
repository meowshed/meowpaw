---
id: TSK-4120
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2300
closes: [REQ-2370, REQ-2388, REQ-3722]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Resolve the posture, check the session's mode at start, and deny what the posture forbids

The `[unattended]` table holds `permission_mode`, `gates`, `release` and
`amend_approved`. `meow-unattended plan` prints the resolved posture and its
deny rules in place of a command line. The start hook refuses a start whose
session mode differs from the declared one, and the guard denies what the
posture forbids, as SPC-1200 states. One task, one branch, one pull request,
one review.

## Acceptance criteria

1. Given a profile whose `[unattended]` table declares all four keys, when
   `meow-unattended plan` runs, then it exits 0 and prints the table, each
   deny rule and the limits of the deny rules, and no `claude -p` line
   (REQ-2370, REQ-2388). Closed by: a fixture naming REQ-2388, seen failing
   first.
2. Given each state in SPC-1200's failure table, when `plan` runs, then it
   exits 3 with that state's line, and reports every refusal in one run.
   Closed by: one fixture for each line.
3. Given a declared `permission_mode = "dontAsk"` and a hook input whose
   `permission_mode` is `default`, when the start command is submitted, then
   the start is refused with both modes named. Closed by: a fixture naming
   REQ-2388.
4. Given `release = false`, when the posture resolves, then it records that
   the run releases nothing, and a `release` that is neither a string nor
   `false` is refused (REQ-3722). Closed by: a fixture naming REQ-3722.
5. Given an active run, when the guard receives an Edit of
   `.meowpaw/profile.toml`, a `git push origin main` with `[git] trunk = "main"`,
   or an Edit of an approved requirement with `amend_approved = false`, then it
   denies each. Closed by: three fixtures.

## What to do

Change the `unattended` feature's table and `plan`'s output, and drop the
snapshot and the command line. Compile the posture code into the `loop`
feature, so `meow-loop` reads the table without running another unit's
program. Update both units' READMEs and this repository's own
`[unattended]` table. Bump `meow-unattended` and `meow-loop` as a `feat`.

## Depends on

- TSK-4100 (blocking): the start hook this task extends.

## Evidence

Pull request 881. The tests are in `plugins/meow-unattended/tests/test_posture.py`,
class `Posture`, and in `plugins/meow-loop/tests/test_session_run.py`:

- Criterion 1: `test_a_resolved_posture_prints_its_table_its_deny_rules_and_their_limits`.
- Criterion 2: `test_each_refusal_is_reported_with_its_line_and_exit_status_3`,
  with one subtest for each line of SPC-1200's failure table, and
  `test_every_refusal_is_reported_in_one_run`.
- Criterion 3: `PostureAtStart.test_a_session_in_another_mode_is_refused_naming_both`.
- Criterion 4: `test_a_release_of_false_is_printed_as_no_release` and
  `PostureAtStart.test_a_release_of_false_is_recorded_and_other_values_are_refused`.
- Criterion 5:
  `PostureGuard.test_the_guard_denies_the_profile_a_push_to_the_trunk_and_an_approved_record`
  and `PostureGuard.test_amend_approved_lets_the_run_edit_an_approved_record`.

The old tests of the snapshot, the command line and `budget_usd`, `units` and
`merge_protected` were removed in a commit of their own, because ADR-2380
withdrew those behaviours. This repository's profile declares an
`[unattended]` table whose `release` is `false`, because no release command is
declared and a run never guesses one.

## Left alone

What the run decides and reports, which TSK-4130 adds to `/meow-flow:run`.
