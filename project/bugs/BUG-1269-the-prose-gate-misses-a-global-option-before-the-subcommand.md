---
id: BUG-1269
artifact: bug
status: approved
severity: major
violates: REQ-3182
enters: implement
found: 2026-09-29
revised: 2026-09-29
issue: 741
---

# The prose gate misses a publishing command with a global option before its subcommand

`meow-prose-gate` takes the word after `gh` as the command group, so
`gh -R o/r pr create`, `gh --repo o/r issue comment` and
`gh --repo=o/r release create` publish their text unchecked. The hook's `if`
patterns, such as `Bash(gh pr create *)`, name none of these forms, and none
names `git -C dir commit` or `git -c key=value commit` either, though the
program reads both when it is called.

## Reproduction

`main` after #733, with `meow-prose-gate` 0.2.1 built by
`crates/meow/build-units`, on macOS on arm64.

1. Feed `plugins/meow-prose-gate/bin/meow-prose-gate check` a hook event for
   each of `gh -R o/r pr create --title x --body "..."`,
   `gh --repo o/r issue comment 5 --body "..."` and
   `gh --repo=o/r release create v1 --notes "..."`, each text holding
   `the low-hanging fruit`.
2. Feed it `git -C sub commit -m "..."` holding `a silver bullet`.
3. Read the `if` patterns in `plugins/meow-prose-gate/hooks/hooks.json`.

## What the system does

Each `gh` command exits 0 with nothing on standard error. The `git -C`
command exits 2 with a P1 finding, because `publishing` in
`crates/meow/src/prose.rs` skips `git`'s global options, and has no such step
for `gh`. The ten `if` patterns each start with the subcommand, `git commit`
or `gh pr create` and so on, so none names a command that puts an option
first.

I didn't observe Claude Code matching an `if` pattern against these
commands, because no fixture can run Claude Code's matcher. I assume a
pattern matches a command that starts with its text, as the rule syntax
states, so a command with an option first is never routed.

## What it should do, and why

The program should skip `gh`'s `-R` and `--repo` option, with its value,
before it reads the group, as it skips `git`'s. The hook should also route a
command that opens with `gh -R`, `gh --repo`, `git -C` or `git -c`, and let the
program decide whether it publishes. REQ-3182 asks the harness to check every
text before it publishes it, and `-R` is how a publish names another
repository.

## Triage

It enters at implement, because ADR-1600 decides the gate reads each `gh`
command creating or editing a pull request, an issue or a release, and the
program and the hook miss one spelling of those commands. Major, because the
gate lets the text through with no report, and `-R` is common wherever a
session works on a repository other than the current one.

## Closed by

Fixtures in `plugins/meow-prose-gate/tests/test_gate.py`: a blocking
fixture for `gh -R`, `gh --repo`, `git -C` and `git -c` in the table `GATED`,
so the routing check fails until `hooks.json` routes each, and a fixture
showing `gh -R o/r pr list` passes.

## Tasks

- [ ] T-001 TSK-2579 read and route a global option before the subcommand, in
      `crates/meow/src/prose.rs` and `plugins/meow-prose-gate/hooks/hooks.json`
