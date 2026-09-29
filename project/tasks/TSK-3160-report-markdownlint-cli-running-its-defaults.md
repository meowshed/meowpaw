---
id: TSK-3160
artifact: task
status: approved
revised: 2026-09-29
bug: BUG-1322
closes: []
issue: 689
---

# Report markdownlint-cli running its defaults

`meow-markdown check` reports `markdownlint runs its defaults: no configuration
file` where the `lint` verb runs markdownlint-cli and nothing it reads from the
root configures it. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given a `lint` verb running `markdownlint '**/*.md'` and no markdownlint
   configuration, when `check` runs, then it exits 1 with
   `markdownlint runs its defaults: no configuration file`; given instead a
   root `.markdownlintrc`, a root `.markdownlint.jsonc`, or a command naming
   `.config/mdl.json` with `-c`, `--config` or `--config=`, it exits 0
   without that line. Closed by:
   `MarkdownlintCliDefaults.test_criterion_1_markdownlint_cli_with_no_configuration_runs_its_defaults`.
2. Given the same verb with only a `docs/.markdownlint.json`, or with
   `-c=.config/mdl.json`, when `check` runs, then it exits 1 with the same
   line, because markdownlint-cli run from the root reads neither. Closed by:
   `MarkdownlintCliDefaults.test_criterion_2_what_markdownlint_cli_does_not_read_is_no_configuration`.

## What to do

In `findings` in `crates/meow/src/markdown.rs`, where the `lint` command runs
`markdownlint` or `markdownlint-cli`, report the line above unless the command
has a `-c` or `--config` word followed by another word, or a `--config=<path>`
word, or git tracks a `.markdownlint.*` or `.markdownlintrc` at the root
(RES-0295, RES-0296). State the finding in SPC-1195's table under "What
`check` finds" and in `plugins/meow-markdown/README.md`. Raise
`meow-markdown`'s patch version. Write the checks first, in a commit of their
own, and see them fail.

## Depends on

- TSK-3150 (not blocking): both edit `findings`, and TSK-3150 is merged.

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet.

## Left alone

`status`, which still lists a nested `.markdownlint.*` as read by
markdownlint-cli. RES-0296 shows markdownlint-cli run from the root ignores
it, but a run from that directory reads it, and the line names no directory to
run from. Whether to reword it is a change to `status`, outside this defect.
