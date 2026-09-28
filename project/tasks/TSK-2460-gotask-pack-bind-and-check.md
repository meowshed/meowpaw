---
id: TSK-2460
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1560
closes: [REQ-2487]
issue:
---

# Bind the verbs to their Task tasks and check the profile and the includes

`meow-gotask bind` prints a `[verbs]` table binding each verb to the task of
exactly its name as `task --force <name>`, and `meow-gotask check` reports
every block on a task a verb runs and every remote include, as SPC-1150
states. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given tasks `test`, `tests` and a blocked `lint`, when `bind` runs, then
   it prints `test = "task --force test"`, binds nothing else, and prints each
   unbound verb's reason, an internal task as internal. Closed by: fixtures,
   seen failing first.
2. Given a profile whose `test` runs a task that can skip without `--force`,
   when `check` runs, then it exits 1 naming it. Closed by: a fixture.
3. Given a profile whose verbs run an internal, a prompting and a
   variable-requiring task, when `check` runs, then each is reported with its
   block and none as missing. Closed by: fixtures.
4. Given a committed Taskfile with a remote include, when `check` runs, then
   the include is a finding and it exits 1, and the skill forbids writing one.
   Closed by: a fixture naming REQ-2487.

## What to do

Add `bind` and `check` to the `gotask` module, reusing the shared runner
code, and describe both in the skill and the README.

## Depends on

TSK-2450, which ships the unit and `status`.

## Evidence

Not yet.

## Left alone

This repository's profile, which runs no Task task.
