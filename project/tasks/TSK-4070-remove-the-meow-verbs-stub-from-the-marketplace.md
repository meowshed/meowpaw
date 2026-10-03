---
id: TSK-4070
artifact: task
status: approved
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

Not yet. Criterion 4's sentence rests on judgement: the page is prose a person reads, and the reviewer reads the section.

## Left alone

The troubleshooting section on the rename, which the notice in an installed copy points to, and the frozen records that name `meow-verbs`. The `[verbs]` table and the five verb names.
