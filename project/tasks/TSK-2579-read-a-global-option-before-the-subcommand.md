---
id: TSK-2579
artifact: task
status: approved
revised: 2026-09-29
bug: BUG-1269
closes: []
issue: 741
---

# Read and route a publishing command with a global option before its subcommand

Make `meow-prose-gate` skip `gh`'s `-R` and `--repo` option before it reads
the command group, and make its hook route a command that opens with
`gh -R`, `gh --repo`, `git -C` or `git -c`. One task, one branch, one pull
request, one review.

## Acceptance criteria

1. Given `gh -R o/r pr create` and `gh --repo=o/r release create` with an
   idiom from the list in `--body` or `--notes`, when the launcher runs
   `check`, then it exits 2 with a P1 finding quoting the idiom. Closed by:
   `EveryGatedCommand.test_gh_short_repo_option` and
   `EveryGatedCommand.test_gh_long_repo_option` in
   `plugins/meow-prose-gate/tests/test_gate.py`.
2. Given `git -C sub commit` and `git -c user.name=x commit` with an idiom in
   `-m`, when the launcher runs `check`, then it exits 2 with a P1 finding.
   Closed by: `EveryGatedCommand.test_git_directory_option` and
   `EveryGatedCommand.test_git_config_option`.
3. Given `hooks.json`, when the routing check reads its `if` patterns, then
   they equal the commands in the table `GATED`, `gh -R`, `gh --repo`,
   `git -C` and `git -c` among them. Closed by:
   `TheHook.test_each_routed_command_has_a_blocking_fixture`.
4. Given `gh -R o/r pr list --search "the low-hanging fruit"`, when the
   launcher runs `check`, then it exits 0, because the command publishes
   nothing. Closed by:
   `ReadableTexts.test_a_repo_option_before_a_command_that_publishes_nothing`.

## What to do

In `publishing` in `crates/meow/src/prose.rs`, skip `-R` and `--repo` with
their value, and `--repo=...`, between `gh` and the group. Add four `if`
entries to `plugins/meow-prose-gate/hooks/hooks.json`, each running the same
`check`. Write the fixtures first, in a commit of their own, and see them
fail. Name the forms in SPC-1010's section on the gate and in the unit's
README, and raise `meow-prose-gate`'s patch version, with each page's
`describes:`.

## Depends on

Nothing. BUG-1269 is approved.

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet.

## Left alone

`git --git-dir`, `git --work-tree` and other `gh` options placed before the
group, such as `--hostname`: the program reads `git`'s already, and nobody
reported a `gh` publish written that way, so routing them would widen the
hook for a form nobody uses. Whether Claude Code matches an `if` pattern
inside a compound command such as `cd x && git commit`, which no fixture can
observe.
