---
id: BUG-1324
artifact: bug
status: approved
severity: minor
violates: REQ-2454
enters: implement
found: 2026-09-29
revised: 2026-09-29
issue: 721
---

# `meow-markdown check` reads a tool `mise exec` loads as a program the verb runs

`meow-markdown check` reports that a link check declares no `offline`,
`max_retries` or `cache` for a verb that runs no link check, where the verb
loads lychee with `mise exec lychee@0.24.2 -- <command>`. REQ-2454 asks for
the settings of a link check a verb runs, and `mise exec` runs only the
command after `--` (RES-0297), so the finding is false.

## Reproduction

`main` after #713, with `meow-markdown` 0.4.3 built by `crates/meow/build-units`.

1. In a new git repository, track `README.md`, `docs/b.md` and a
   `.meowpaw/profile.toml` holding `[markdown]` with `target = "github"` and
   `[verbs]` with `test = "mise exec lychee@0.24.2 -- python3 -m unittest"`.
2. Run `plugins/meow-markdown/bin/meow-markdown check`.

## What the system does

`check` exits 1 and prints `link check declares no offline`,
`link check declares no max_retries` and `link check declares no cache`. The
cause is `program` in `crates/meow/src/markdown.rs`, which removes an
`@<version>` suffix from every word, so `lychee@0.24.2` reads as a lychee run.
The same reading makes a markdownlint front end that `mise exec` loads in the
`lint` verb count as the linter the verb runs.

I found it when TSK-3170 ran this repository's Markdown suite under
`mise exec lychee@0.24.2 --`: `Adopted.test_criterion_7_check_passes_on_this_repository`
failed with the three lines above.

## What it should do, and why

`check` should read the words between `mise exec` or `mise x` and its `--`,
or its `-c` flag, as mise's own, and read the command after them as the run,
because mise loads those tools onto `PATH` and runs none of them (RES-0297). A
check that reports a finding a repository doesn't have gets switched off, and
then it catches nothing.

## Triage

It enters at implement, because REQ-2454 and SPC-1195 are right and `check`
misreads the command. Minor, because the false finding is visible and blocks
nothing that works, but it keeps TSK-3170 from running the real lychee in this
repository's `test` verb.

## Closed by

A fixture in `plugins/meow-markdown/tests/test_markdown.py` for a verb that
loads lychee with `mise exec` and runs another program, and one that runs
lychee after `--`, and the rule in SPC-1195's paragraph on what a command
runs.

## Tasks

- [x] T-001 TSK-3180 read the tools `mise exec` loads as no run, in
      `crates/meow/src/markdown.rs`
      evidence: 2 checks seen failing first, 56 `meow-markdown` fixtures
      passing, in #724.
