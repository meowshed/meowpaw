---
id: TSK-4925
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2525
closes: [REQ-1426]
issue: 968
projected: a0e8c8f5a54f
tracked: ae40851556c4
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Deny from a hook whose binary is missing, naming the install command

Every blocking hook's launcher denies the call with exit 2 when no binary
exists for the machine, naming the unit, the target and the command that
installs the unit again, as SPC-1240 states under "A hook whose program is
missing" and SPC-1060 and SPC-1010 state for their units. One task, one
branch, one pull request, one review: the tests first, then the change, its
documentation and its marks.

## Acceptance criteria

1. Given `meow-git`'s launcher with no binary beside it, when it runs as
   `commit-guard` or `push-guard`, then it exits 2 and its standard error
   names `meow-git`, the machine's target and
   `claude plugin install meow-git@meowpaw` (REQ-1426). Closed by: the unit's
   fixture with no binary, changed from "lets the command through" and seen
   failing first.
2. Given the launchers of `meow-prose-gate`, `meow-github` and `meow-loop`
   with no binary, when each runs its hook subcommand, then each exits 2 with
   the same three facts for its unit (REQ-1426). Closed by: each unit's
   fixture with no binary.
3. Given `meow-flow`'s launcher with no binary, when it runs as the
   `SessionStart` hook, then it prints that the record wasn't checked and the
   install command, and exits 0; given `meow-checks revision` with no binary,
   it prints the same for its unit and exits 0. Closed by: each unit's
   fixture.
4. Given `meow-git`'s binary and no `meow-scm`, when `push-guard` runs, then
   the push goes through and the message check is reported unrun for every
   commit (REQ-0079). Closed by: the existing fixture, kept passing.
5. Given a task in `mise.toml` that the gate runs, when its tool isn't
   installed, then it exits non-zero naming the tool (REQ-1426). Closed by: a
   test under `tools/` over each gate task.

## What to do

Change the launchers under `plugins/meow-git/bin/`, `plugins/meow-prose-gate/bin/`,
`plugins/meow-github/bin/` and `plugins/meow-loop/bin/`, and the units' README
sentences that say a missing binary lets each command through. Keep each
launcher under the shell verbs SPC-1080 states. A launcher with no binary
denies every call its hook matches, because it can't tell which one its
program would have let through, and each README says so as the cost
ADR-2710 names.

## Depends on

Nothing.

## Evidence

The launchers of `meow-git`, `meow-prose-gate`, `meow-github` and `meow-loop` deny with exit 2 and
name the unit, the machine and the install command, and that landed with TSK-5165 in pull request 1047,
whose tests close criteria 1, 2 and 4: `test_a_missing_binary_names_the_machine_and_the_reinstall`
and the fixtures of the three other units, and the `meow-scm` case that stays as it was. The command
they name is `claude plugin install meow-core@meowpaw`, where this task wrote
`meow-git@meowpaw`, because `meow-core` ships the shared binary and reinstalling the unit
doesn't restore it. The tests of this pull request came first, in a commit of their own:
`test_a_missing_binary_at_session_start_says_so_and_lets_the_session_begin` in
`plugins/meow-flow/tests/test_record.py` failed, because `paw status --waiting` printed nothing,
and closes criterion 3 for `meow-flow`; `meow-checks revision` printed its message and exited 0
already, in pull request 1047. `tools/test_gate_tasks.py` closes criterion 5: no task of
`mise.toml` ends in `|| true`, tests whether a tool exists and skips, or hides a failure and falls
through, so a missing tool fails a task with the shell's own message naming it. It can fail:
its first test runs it on three spellings that do. `mise run all` passed with exit status 0.

## Left alone

The prose gate's judge failing to run, which keeps its not-checked message
under REQ-3748, and what a verb reports when its tool is missing, which
SPC-1040 states as an unresolved verb.
