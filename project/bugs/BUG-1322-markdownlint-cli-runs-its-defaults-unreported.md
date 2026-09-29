---
id: BUG-1322
artifact: bug
status: approved
severity: minor
violates: REQ-2434
enters: implement
found: 2026-09-29
revised: 2026-09-29
issue: 689
---

# `meow-markdown check` misses markdownlint-cli running its defaults

`meow-markdown check` exits 0 with `no findings` where the `lint` verb runs
markdownlint-cli and nothing configures it, although markdownlint-cli then
runs its default rules and says nothing about it. REQ-2434 asks the pack to
report an absent setting behind a verb, and `check` already does so for
markdownlint-cli2 in the same state.

## Reproduction

`main` after #697, with `meow-markdown` 0.4.2 built by `crates/meow/build-units`.

1. In a new git repository, commit `README.md`, `docs/b.md` and a
   `.meowpaw/profile.toml` holding `[markdown]` with `target = "github"` and
   `[verbs]` with `lint = "markdownlint '**/*.md'"`.
2. Run `plugins/meow-markdown/bin/meow-markdown check`.

## What the system does

`check` exits 0 and prints `no findings`. `findings` in
`crates/meow/src/markdown.rs` reports defaults for markdownlint-cli2 alone.
markdownlint-cli 0.49.1 on the same files reports MD013 against the default
limit of 80, and prints no line saying no configuration was found (RES-0295).

## What it should do, and why

`check` should exit 1 with `markdownlint runs its defaults: no configuration
file` where the `lint` command runs markdownlint-cli, names no configuration
with `-c <path>`, `--config <path>` or `--config=<path>`, and git tracks no
`.markdownlint.*` or `.markdownlintrc` at the root. Those are the places
markdownlint-cli run from the root takes its rules from (RES-0295, RES-0296),
and the defaults run unseen otherwise, which is what REQ-2434 asks the pack to
report.

## Triage

It enters at implement. REQ-2434 covers the case, and ADR-1900 names only
markdownlint-cli2's defaults because RES-0294 never ran markdownlint-cli with
no configuration. SPC-1195 is living, so it states the finding without a new
decision. Minor, because the repository still lints, only with rules it didn't
choose.

## Closed by

The reproduction as fixtures in `plugins/meow-markdown/tests/test_markdown.py`,
in the class `MarkdownlintCliDefaults`.

## Tasks

- [ ] T-001 TSK-3160 report markdownlint-cli running its defaults, in
      `crates/meow/src/markdown.rs`
