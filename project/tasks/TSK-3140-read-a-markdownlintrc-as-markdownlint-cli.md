---
id: TSK-3140
artifact: task
status: approved
revised: 2026-09-29
bug: BUG-1320
closes: []
issue: 687
---

# Read a `.markdownlintrc` as a markdownlint-cli configuration in `status` and `bind`

`meow-markdown status` lists a tracked `.markdownlintrc` as read by
markdownlint-cli alone, and `bind` binds `lint` to markdownlint-cli where a
root `.markdownlintrc` is the only markdownlint configuration. One task, one
branch, one pull request, one review.

## Acceptance criteria

1. Given a repository tracking `README.md`, `docs/b.md` and a root
   `.markdownlintrc`, and no other linter configuration, when `bind` runs,
   then it prints `lint = "markdownlint '**/*.md'"` followed by a comment
   naming `meow-markdown check`, and doesn't print
   `lint = "meow-markdown check"`. Closed by:
   `Markdownlintrc.test_criterion_1_a_markdownlintrc_binds_markdownlint_cli`.
2. Given the same repository, when `status` runs, then it exits 0, lists
   `.markdownlintrc` as read by markdownlint-cli alone, and doesn't print
   `markdownlint configuration: none tracked`. Closed by:
   `Markdownlintrc.test_criterion_2_status_lists_a_markdownlintrc`.

## What to do

In `crates/meow/src/markdown.rs`, have `status` list each tracked
`.markdownlintrc` among the markdownlint configuration files, read by
markdownlint-cli alone when it runs in that file's directory, because
markdownlint-cli doesn't read one below the directory it runs from
(RES-0295). Have `bind` print `lint = "markdownlint '**/*.md'"`, with the same
comment naming `meow-markdown check`, where a root `.markdownlintrc` exists and
no `.markdownlint-cli2.*` or `.markdownlint.*` file does. Keep a
`.markdownlint.*` or `.markdownlint-cli2.*` file binding markdownlint-cli2,
because markdownlint-cli2 reads both families. Leave `check` as it is: its
findings about markdownlint-cli are separate defects, #688 and #689.

State the file in SPC-1195's sections on `status` and `bind`, and in
`plugins/meow-markdown/README.md`. Raise `meow-markdown`'s patch version. Write
the checks first, in a commit of their own, and see them fail.

## Depends on

Nothing. BUG-1320 is approved.

## Cover

- Checks: plugins/meow-markdown/tests/test_markdown.py
- Failing run: project/evidence/b92cd9bb18ec.txt
- Landed in: #693
- Judgement: none

## Evidence

`Corpus::markdownlintrc` in `crates/meow/src/markdown.rs` lists each tracked
`.markdownlintrc`. `status` prints it as read by markdownlint-cli alone, run
in its directory, and `bind` prints `lint = "markdownlint '**/*.md'"` with the
comment naming `meow-markdown check` where a root `.markdownlintrc` is the only
markdownlint configuration. SPC-1195 and `plugins/meow-markdown/README.md`
state the file, and `meow-markdown` goes to 0.4.1.

The two checks in the class `Markdownlintrc` failed first: `meow-verbs run
test` exited 1 with `FAILED (failures=2, skipped=1)` in the Markdown suite,
kept as `project/evidence/b92cd9bb18ec.txt`, in the commit that held the
checks alone. They pass now:

```text
$ python3 -m unittest test_markdown    # in plugins/meow-markdown/tests
Ran 49 tests
OK (skipped=1)                         # exit 0
```

`meow-verbs evidence --keep format lint check test build` exits 0 on this
change's own tree, each result kept in `project/evidence/`, as the pull
request cites.

## Left alone

`check`, because its markdownlint-cli findings are separate defects, #688 and #689,
and each defect is closed by its own change.
