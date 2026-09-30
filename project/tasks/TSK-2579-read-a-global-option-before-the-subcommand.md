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

## Evidence

`publishing` in `crates/meow/src/prose.rs` now skips `-R` and `--repo` with
their value, `--repo=...` and an attached `-R...`, between `gh` and the
group. `plugins/meow-prose-gate/hooks/hooks.json` gains four `if` entries,
`Bash(gh -R *)`, `Bash(gh --repo *)`, `Bash(git -C *)` and `Bash(git -c *)`,
each running the same `check`. SPC-1010's section on the gate and the unit's
README name the forms, the README says the hook now also runs on a command
that publishes nothing, and `meow-prose-gate` goes to 0.2.2, with the
`describes:` of its README, `docs/README.md` and `docs/troubleshooting.md`.

Three checks failed first, in the commit that held the fixtures alone:
`meow-verbs run test` exited 1 with `FAILED (failures=3)`, naming the two
`gh` fixtures and the routing check, kept as
the run in #743, no longer kept. They pass now:

```text
$ python3 -m unittest test_gate    # in plugins/meow-prose-gate/tests
Ran 42 tests
OK                                 # exit 0
```

That Claude Code routes `gh -R owner/repo pr create` through the new
`Bash(gh -R *)` entry is assumed from the rule syntax and not observed,
because no fixture runs Claude Code's matcher.

`meow-verbs evidence --keep format lint check test build` exits 0 on this
change's own tree, each result kept in `project/evidence/`, as the pull
request cites.

## Left alone

`git --git-dir`, `git --work-tree` and other `gh` options placed before the
group, such as `--hostname`: the program reads `git`'s already, and nobody
reported a `gh` publish written that way, so routing them would widen the
hook for a form nobody uses. Whether Claude Code matches an `if` pattern
inside a compound command such as `cd x && git commit`, which no fixture can
observe.
