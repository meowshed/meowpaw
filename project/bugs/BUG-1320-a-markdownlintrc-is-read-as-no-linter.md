---
id: BUG-1320
artifact: bug
status: approved
severity: minor
violates: REQ-2352
enters: implement
found: 2026-09-29
revised: 2026-09-29
issue: 687
---

# `meow-markdown` binds `lint` to its own check beside a `.markdownlintrc`

`meow-markdown bind` prints `lint = "meow-markdown check"` in a repository
whose only linter configuration is a root `.markdownlintrc`, and `status`
prints that no markdownlint configuration is tracked. So the binding drops the
linter the repository configured, which REQ-2352 asks the pack to resolve.

## Reproduction

`main` after #681, with `meow-markdown` 0.4.0 built by `crates/meow/build-units`.

1. In a new git repository, commit `README.md`, `docs/b.md`, a
   `.meowpaw/profile.toml` holding `[markdown]` with `target = "github"`, and
   a `.markdownlintrc` holding `{ "MD013": false }`.
2. Run `plugins/meow-markdown/bin/meow-markdown bind`, then `status`.

## What the system does

`bind` exits 0 and prints `lint = "meow-markdown check"`, the row SPC-1195
keeps for a repository with no linter configuration of any kind. `status`
prints `markdownlint configuration: none tracked`. `detected` in
`crates/meow/src/markdown.rs` counts every `.markdownlint*` file, but
`Corpus::markdownlint` lists only `.markdownlint-cli2.*` and `.markdownlint.*`,
so the program detects a corpus from a file it then reports as absent.

## What it should do, and why

`bind` should print `lint = "markdownlint '**/*.md'"` with the comment naming
`meow-markdown check`, and `status` should list the file as read by
markdownlint-cli alone. markdownlint-cli 0.49.1 reads a root `.markdownlintrc`
and markdownlint-cli2 0.23.2 ignores it (RES-0295), so markdownlint-cli is the
front end this repository configured. Binding markdownlint-cli2 would run the
default rules the repository turned off.

## Triage

It enters at implement. REQ-2352 is right, and ADR-1900's lint row names the
two configuration families RES-0294 observed, which didn't include this file.
SPC-1195 is living, so it states the third file without a new decision.
Minor, because a repository with a `.markdownlintrc` gets a wrong binding it
reads before pasting, and no verb runs until someone pastes it.

## Closed by

The reproduction as fixtures in `plugins/meow-markdown/tests/test_markdown.py`,
in the class `Markdownlintrc`: `bind` binds markdownlint-cli beside a root
`.markdownlintrc`, and `status` lists the file as read by markdownlint-cli
alone.

## Tasks

- [x] T-001 TSK-3140 read a `.markdownlintrc` as a markdownlint-cli
      configuration in `status` and `bind`, in `crates/meow/src/markdown.rs`
      evidence: 2 checks seen failing first, 49 `meow-markdown` fixtures
      passing, in #693.
