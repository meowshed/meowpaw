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

- Checks: plugins/meow-markdown/tests/test_markdown.py
- Failing run: project/evidence/6c535d226ae5.txt
- Landed in: #697
- Judgement: none

## Evidence

`program` in `crates/meow/src/markdown.rs` names a word's program by its last
path component without an `@<version>` suffix, and both `programs` and the
link check's reading use it. `findings` treats `markdownlint-cli` as
markdownlint-cli, and `names_a_config` counts a `--config` word followed by
another word as markdownlint-cli2's configuration. SPC-1195 and
`plugins/meow-markdown/README.md` state both readings, and `meow-markdown`
goes to 0.4.2.

The three checks in the class `LintCommand` failed first: `meow-verbs run
test` exited 1 with `FAILED (failures=3, skipped=1)` in the Markdown suite,
kept as `project/evidence/6c535d226ae5.txt`, in the commit that held the
checks alone. The `--config=<path>` case in criterion 1 passed before the fix
as well, because it guards the reading the fix must keep. They pass now:

```text
$ python3 -m unittest test_markdown    # in plugins/meow-markdown/tests
Ran 52 tests
OK (skipped=1)                         # exit 0
```

`meow-verbs evidence --keep format lint check test build` exits 0 on this
change's own tree, each result kept in `project/evidence/`, as the pull
request cites.

## Left alone

markdownlint-cli running its defaults, which is a separate defect, #689.
markdownlint-cli's own `-c` and `--config` flags belong with that defect,
because only its defaults finding reads them.
