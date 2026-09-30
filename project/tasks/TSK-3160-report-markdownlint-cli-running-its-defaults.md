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

## Evidence

`findings` in `crates/meow/src/markdown.rs` reports
`markdownlint runs its defaults: no configuration file` where the `lint`
command runs `markdownlint` or `markdownlint-cli`, `names_a_cli_config` finds
no `-c <path>`, `--config <path>` or `--config=<path>`, and git tracks no
`.markdownlint.*` or `.markdownlintrc` at the root. RES-0296 records the two
observations the rule needed beyond RES-0295. SPC-1195 and
`plugins/meow-markdown/README.md` state the finding, and `meow-markdown` goes
to 0.4.3.

The two checks in the class `MarkdownlintCliDefaults` failed first, three
cases between them: `meow-verbs run test` exited 1 with
`FAILED (failures=3, skipped=1)` in the Markdown suite, seen in
the run under #703, whose output is no longer kept, in the commit that held the checks alone.
The five configured cases in criterion 1 passed before the fix as well,
because they guard against a finding the tool doesn't have. They pass now:

```text
$ python3 -m unittest test_markdown    # in plugins/meow-markdown/tests
Ran 54 tests
OK (skipped=1)                         # exit 0
```

`meow-verbs evidence --keep format lint check test build` exits 0 on this
change's own tree, each result kept in `project/evidence/`, as the pull
request cites.

## Left alone

`status`, which still lists a nested `.markdownlint.*` as read by
markdownlint-cli. RES-0296 shows markdownlint-cli run from the root ignores
it, but a run from that directory reads it, and the line names no directory to
run from. Whether to reword it is a change to `status`, outside this defect.
