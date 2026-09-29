---
id: BUG-1321
artifact: bug
status: approved
severity: minor
violates: REQ-2434
enters: implement
found: 2026-09-29
revised: 2026-09-29
issue: 688
---

# `meow-markdown check` misreads the program and the flags the lint verb runs

`meow-markdown check` compares each word of the `lint` command whole and
ignores its `--config` flag, so it reports defaults a named configuration
replaced, and misses a front end named with its version. REQ-2434 asks the
pack to read the settings behind a verb, and a wrong reading reports a finding
that isn't there and hides one that is.

## Reproduction

`main` after #693, with `meow-markdown` 0.4.1 built by `crates/meow/build-units`.
Each case is a new git repository tracking `README.md`, `docs/b.md` and a
`.meowpaw/profile.toml` holding `[markdown]` with `target = "github"` and the
`lint` verb given, and `plugins/meow-markdown/bin/meow-markdown check` runs in
it.

1. `lint = "markdownlint-cli2 --config .config/mdl.jsonc '**/*.md'"`, with a
   tracked `.config/mdl.jsonc` holding `{ "MD013": false }`.
2. `lint = "npx --yes markdownlint-cli2@0.23.2 '**/*.md'"`, with no
   configuration file.
3. `lint = "npx markdownlint-cli@0.49.1 '**/*.md'"`, with a tracked
   `.markdownlint-cli2.jsonc`.

## What the system does

Case 1 exits 1 with `markdownlint-cli2 runs its defaults: no configuration
file`, although markdownlint-cli2 0.23.2 applied the named file: 0 issues with
it and 2 without (RES-0295). Case 2 exits 0 with `no findings`, because
`programs` in `crates/meow/src/markdown.rs` yields the word
`markdownlint-cli2@0.23.2` and `findings` compares it with `markdownlint-cli2`
by equality. Case 3 exits 0 with `no findings` for the same reason, and because
`findings` knows the older front end only by its program name `markdownlint`,
never by its package name `markdownlint-cli`.

## What it should do, and why

Case 1 should exit 0, because the configuration file the command names is the
setting REQ-2434 asks about, and it's present. A `--config=<path>` word
should still count as no configuration, because markdownlint-cli2 reads it as
a glob (RES-0295). Case 2 should exit 1 with the defaults finding, and case 3
with `markdownlint ignores .markdownlint-cli2.jsonc`, because `npx` runs the
word with its version removed (RES-0295), and `npx markdownlint-cli` runs
markdownlint-cli.

## Triage

It enters at implement, because REQ-2434 and SPC-1195's rule for reading a
command are right, and the program reads fewer forms than that rule covers.
Minor, because each case needs a lint verb written in one particular form,
and the wrong line names the file or the program, so a reader can check it.

## Closed by

The reproduction as fixtures in `plugins/meow-markdown/tests/test_markdown.py`,
in the class `LintCommand`.

## Tasks

- [x] T-001 TSK-3150 read a program word without its version and
      markdownlint-cli2's `--config`, in `crates/meow/src/markdown.rs`
      evidence: 3 checks seen failing first, 52 `meow-markdown` fixtures
      passing, in #697.
