---
id: TSK-3830
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-2200
closes: [REQ-3614]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Remove kept evidence from the repository and from `meow-verbs`

`project/evidence/` is gone, `meow-verbs evidence --keep` is removed with a message saying so, and no `paw check` rule asks a task for a kept file. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the repository, when the change lands, then `project/evidence/` doesn't exist. Closed by: `test -e project/evidence` exiting 1.
2. Given `meow-verbs evidence --keep test`, when it runs, then it exits 2 saying kept evidence was removed by ADR-2300 and writes nothing. Closed by: a `meow-verbs` fixture test.
3. Given a task whose Evidence names checks and a pull request and no file, when `paw check` runs, then it reports nothing. Closed by: a fixture test.

## What to do

Change `crates/meow/src/verbs.rs` or wherever `--keep` lives, `plugins/meow-verbs/`, `.meowpaw/profile.toml` if it names an evidence directory, and delete `project/evidence/`. Git history keeps the files.

## Depends on

Nothing.

## Cover

Not yet. The cover step replaces this line with four, `Checks`,
`Failing run`, `Landed in` and `Judgement`, and `paw ready implement` refuses
the task until they are filled.

## Evidence

`NoKeptEvidence` in `plugins/meow-verbs/tests/test_verbs.py` holds seven
checks for criterion 2, the tree id and `tree <commit>`, three of them added
with the review's fixes, and `tools/test_no_kept_evidence.py`
holds two for criterion 1. The six in the pull request's first commit failed there.
Criterion 3 needed no new check: `paw check` asks no task for a kept file
since TSK-3810 removed the Cover gate, and it reports 0 findings on this
record, whose tasks name checks and pull requests. The pull request deletes
the 577 files of `project/evidence/`, which git history keeps.
`meow-verbs run format lint check test` passed all four verbs.

Left alone: records that cite a kept file by its path keep the citation until
TSK-3860 rewrites it.

## Left alone

The in-flight worktrees for TSK-2703, TSK-2950, TSK-3350 and TSK-3700 are
postponed by the owner and left as they are.
