---
id: TSK-3180
artifact: task
status: approved
revised: 2026-09-29
bug: BUG-1324
closes: []
issue: 721
---

# Read the tools `mise exec` loads as no program the verb runs

`meow-markdown check` leaves out the words between `mise exec` or `mise x`
and its `--`, or its `-c` flag, when it reads which programs a verb runs,
because those words are tools mise loads and not programs it runs (RES-0297).
One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given a `test` verb running
   `mise exec lychee@0.24.2 -- python3 -m unittest` and no `lychee.toml`,
   when `check` runs, then it exits 0 with no `link check declares no` line;
   given `mise x lychee@0.24.2 -- lychee '**/*.md'`, it exits 1 naming each
   of the three settings. Closed by:
   `LinkSettings.test_a_tool_mise_exec_loads_is_no_link_check`.
2. Given a `lint` verb running
   `mise exec markdownlint-cli2@0.23.2 -- prettier --check .` and no
   markdownlint configuration, when `check` runs, then it exits 0 with no
   defaults line; given the same verb running `markdownlint-cli2 '**/*.md'`
   after `--`, it exits 1 with
   `markdownlint-cli2 runs its defaults: no configuration file`. Closed by:
   `LintCommand.test_a_tool_mise_exec_loads_is_no_linter`.

## What to do

In `crates/meow/src/markdown.rs`, drop the words `mise exec` or `mise x`
takes before its command from the words `programs` and `link_settings` read,
up to the first `--`, `-c` or `--command`. Say the rule in SPC-1195's
paragraph on what a command runs, citing RES-0297. Write the checks first, in
a commit of their own, and see them fail. Raise `meow-markdown` to 0.4.4, a
fix, with its README's `describes:`.

## Depends on

Nothing. BUG-1324 is approved.

## Evidence

`words` in `crates/meow/src/markdown.rs` leaves out the words `mise exec` or
`mise x` takes before its command, up to and including `--`, `-c` or
`--command`. `programs` and `link_settings` both read a command through
`words`, so the rule holds for the linter and the link check alike. SPC-1195
states it, citing RES-0297, and `meow-markdown` is 0.4.4 with its README's
`describes:`.

```text
$ python3 -m unittest test_markdown    # in plugins/meow-markdown/tests
Ran 56 tests
OK (skipped=1)                         # exit 0; the skip is the real-lychee fixture, which TSK-3170 makes run
```

`meow-verbs evidence --keep format lint check test build` exits 0 on this
change's own tree, each result kept in `project/evidence/`, as the pull
request cites.

## Left alone

Other wrappers that load a tool without running it, such as `npx -p`,
because no verb in a known repository uses one and no research records their
grammar.
