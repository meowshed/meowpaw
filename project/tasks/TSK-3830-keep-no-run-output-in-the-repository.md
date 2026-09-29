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

Not yet.

## Left alone

The in-flight worktrees for TSK-2703, TSK-2950, TSK-3350 and TSK-3700 are
postponed by the owner and left as they are.
