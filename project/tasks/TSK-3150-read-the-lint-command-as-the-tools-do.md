---
id: TSK-3150
artifact: task
status: approved
revised: 2026-09-29
bug: BUG-1321
closes: []
issue: 688
---

# Read the lint command's program and `--config` flag as the tools do

`meow-markdown check` names a program by its word with any `@<version>`
removed, counts `markdownlint-cli` as markdownlint-cli, and takes the file
markdownlint-cli2's `--config` names as its configuration. One task, one
branch, one pull request, one review.

## Acceptance criteria

1. Given a `lint` verb running
   `markdownlint-cli2 --config .config/mdl.jsonc '**/*.md'` and no
   `.markdownlint*` file, when `check` runs, then it exits 0 with no defaults
   finding; given the same verb written with `--config=.config/mdl.jsonc`, it
   exits 1 with the defaults finding. Closed by:
   `LintCommand.test_criterion_1_a_config_flag_names_the_configuration`.
2. Given a `lint` verb running `npx --yes markdownlint-cli2@0.23.2 '**/*.md'`
   and no configuration file, when `check` runs, then it exits 1 with the
   defaults finding. Closed by:
   `LintCommand.test_criterion_2_a_versioned_cli2_is_read`.
3. Given a `lint` verb running `npx markdownlint-cli@0.49.1 '**/*.md'` beside a
   tracked `.markdownlint-cli2.jsonc`, when `check` runs, then it exits 1 with
   `markdownlint ignores .markdownlint-cli2.jsonc`. Closed by:
   `LintCommand.test_criterion_3_a_versioned_markdownlint_cli_is_read`.

## What to do

In `crates/meow/src/markdown.rs`, name each program in a command by its last
path component with any `@<version>` suffix removed, and use that one reading
wherever a command's program is compared, the link check's included. Treat
`markdownlint` and `markdownlint-cli` as markdownlint-cli. Where the `lint`
command runs markdownlint-cli2 and a word `--config` is followed by another
word, count that configuration as present, and don't count a
`--config=<path>` word, because markdownlint-cli2 reads it as a glob
(RES-0295).

State both readings in SPC-1195's section on `check` and in
`plugins/meow-markdown/README.md`. Raise `meow-markdown`'s patch version.
Write the checks first, in a commit of their own, and see them fail.

## Depends on

- TSK-3140 (not blocking): both edit `crates/meow/src/markdown.rs`, and
  TSK-3140 is merged.

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet.

## Left alone

markdownlint-cli running its defaults, which is a separate defect, #689.
markdownlint-cli's own `-c` and `--config` flags belong with that defect,
because only its defaults finding reads them.
