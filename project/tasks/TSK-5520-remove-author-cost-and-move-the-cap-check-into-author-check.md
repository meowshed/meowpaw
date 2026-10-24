---
id: TSK-5520
artifact: task
status: done
revised: 2026-10-11
epic: EPC-2820
closes: [REQ-1060]
issue: 1103
projected: 49f10cf0a285
tracked: 7ef61a531b4f
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Remove `author cost` and move the platform-cap check into `author check`

The native tool loses the `cost` subcommand and every read of a
`budget.toml`, and keeps the platform's cap of 1,536 characters on a
description under the check that already reads every description. The gate
loses the `budget` task and its binding into the `lint` stage.

## Acceptance criteria

1. Given `crates/meow/src/author.rs`, when the crate is built and its tests
   run, then no `cost` subcommand exists, no code reads `budget.toml`, and
   `author check` fails a fixture unit whose skill description exceeds 1,536
   characters. Closed by: the tests in `plugins/meow-author/tests/`, seen
   failing first for the cap case.
2. Given `mise.toml` and `.meowpaw/profile.toml`, when `mise run all` runs,
   then no `budget` task runs, the `lint` stage names none, and the gate
   passes as far as its pre-existing findings allow. Closed by: the gate's
   output in the pull request.

## What to do

Delete the `cost` function, its dispatch line, its `determines`/`by_hand`
entry and the `ceiling` read; add the cap check to `check` over the same
pieces `cost` counted. Remove the `budget` task from `mise.toml` and from
`all`'s depends list, and the `budget` stage call from the profile's `lint`
line. Update `plugins/meow-author/tests/test_author.py`: the budget cases go,
a cap case in `author check` arrives. Update `tools/test_secrets_rule.py`: the
budget criterion goes, the rule test stays. SPC-1080's `author` table and
SPC-1030's command table lose their `cost` rows in TSK-5530's documentation
pass where they name the budget.

## Depends on

- TSK-5510 (not blocking): the requirement the cap check keeps is written by
  the other task, which runs in parallel.

## Evidence

The `cost` subcommand and the `ceiling` read are gone from
`crates/meow/src/author.rs`, and `check` holds the platform cap over the same
pieces `cost` counted: `test_a_description_over_the_platform_cap_fails` in
`plugins/meow-author/tests/test_author.py` failed first against the tree
without the check, and passes with it (criterion 1, REQ-1060). The `budget`
task is gone from `mise.toml` and from `.meowpaw/profile.toml`'s `lint` line,
and the gate runs none of it (criterion 2). The unit's 54 tests pass, and
`tools/test_secrets_rule.py` lost its budget criterion and keeps the rule
test.

## Left alone

The request budget in the GitHub layer and the run bounds in the runner,
which are different mechanisms, and `tools/check_budget.py`, which ADR-1460
already removed.
