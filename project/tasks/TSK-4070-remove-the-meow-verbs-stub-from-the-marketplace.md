---
id: TSK-4070
artifact: task
status: done
revised: 2026-10-03
realises: ADR-2360
closes: [REQ-3004, REQ-3654]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Remove the `meow-verbs` stub from the marketplace

`plugins/meow-verbs/` and its marketplace entry are gone, and no live page lists the stub. One task, one branch, one pull request, one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given the marketplace, when `.claude-plugin/marketplace.json` is read, then it has no `meow-verbs` entry. Closed by: a check in `tools/test_marketplace.py`.
2. Given the repository, when `git ls-files plugins/meow-verbs` runs, then it prints nothing. Closed by: the same check.
3. Given the tracked files outside `project/`, when they are searched for `meow-verbs`, then only `docs/troubleshooting.md`, SPC-1040's sentence about the rename and `tools/test_marketplace.py` name it. Closed by: `test_only_the_stub_names_the_old_unit` in `tools/test_marketplace.py`, narrowed to those three.
4. Given `docs/troubleshooting.md`, when its `describes` list is read, then it names no `meow-verbs` version, and its section on the rename says an install made before the removal still prints the notice. Closed by: `python3 tools/check_docs.py` for the list, and judgement for the sentence, because the page is prose a person reads.
5. Given this change's tree, when `meow-checks run format lint check test build` runs, then each passes. Closed by: each verb's outcome in the task's pull request.

## What to do

Delete `plugins/meow-verbs/`, its entry in `.claude-plugin/marketplace.json` and its row in `docs/README.md`. Drop `meow-verbs@0.9.0` from the `describes` list of `docs/troubleshooting.md` and say in its section on the rename that the stub left the marketplace and an earlier install still prints the notice. Replace the check that the stub exists with the two checks in criteria 1 and 2, and narrow the check of where the old name may appear. Frozen records keep the name.

Write the checks first, in a commit of their own, and see them fail.

## Depends on

Nothing.

## Evidence

`python3 -m unittest tools/test_marketplace.py` reports `Ran 7 tests` and `OK`
on this change, and `meow-checks run format lint check test build` passes all
five verbs, as this task's pull request, #810, shows. The checks came first, in
the pull request's first commit, where three of them failed:
`test_the_marketplace_lists_no_meow_verbs` closes criterion 1,
`test_git_tracks_nothing_under_meow_verbs` closes criterion 2, and
`test_only_the_stub_names_the_old_unit`, narrowed to the troubleshooting page
and the check file, closes criterion 3. `python3 tools/check_docs.py` closes the
first half of criterion 4: it reports `19 pages, 0 documentation failures` with
`meow-verbs@0.9.0` gone from the `describes` list.

The second half of criterion 4 rests on judgement, because the page is prose a
person reads. The reviewing agent read the section and found it states the
cached-copy consequence with its reason in one sentence.

The same review found two low items in `tools/test_marketplace.py`, a module
docstring that named only TSK-3870 and a `named` entry that read as a fourth
file naming the unit. Both are fixed by a docstring and a comment. The test
that stood for the removed stub check, `test_meow_verbs_is_a_stub_that_names_its_replacement`,
is deleted, because the stub it described is gone, and criterion 2's check holds
the tracked-files half of it.

## Left alone

The troubleshooting section on the rename, which the notice in an installed copy points to, and the frozen records that name `meow-verbs`. The `[verbs]` table and the five verb names.
