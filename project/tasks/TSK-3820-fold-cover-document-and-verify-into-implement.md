---
id: TSK-3820
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-2200
closes:
  [
    REQ-3606,
    REQ-3612,
    REQ-3616,
    REQ-3618,
    REQ-3624,
    REQ-3626,
    REQ-3628,
    REQ-3640,
    REQ-3642,
    REQ-3644,
    REQ-3650,
  ]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Rewrite the method's prompts and templates for the seven-step chain

The method skill names seven steps and dispatches no record reviewer, `steps/implement.md` writes the tests first and carries the documentation and the record marks, `steps/review.md` is a code review inside the pull request that reports a test that can't fail, and the verify, document and cover step files go. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given `plugins/meow-flow/skills/method/`, when a static fixture reads it, then `SKILL.md` names the seven steps in order and `steps/` holds exactly one file for each. Closed by: `MethodSkill` fixture tests.
2. Given the files under `plugins/meow-flow/`, when a static fixture searches them, then none dispatches `record-reviewer` or `skeptic`, and `agents/record-reviewer.md` is gone. Closed by: a fixture test.
3. Given `steps/implement.md`, when a static fixture reads it, then it asks for a test per checkable criterion in a first commit that fails, for no weakening of those tests outside a commit saying why, and for the documentation and the record marks in the same pull request. Closed by: a fixture test.
4. Given `steps/review.md`, when a static fixture reads it, then it names a code review in the pull request that fixes its findings there, writes nothing into the record, and reports a test that would pass against a wrong implementation. Closed by: a fixture test.
5. Given the task and epic templates, when `paw template task` and `paw template epic` run, then the task has no `## Cover` and the epic no `checked-at`. Closed by: a fixture test.
6. Given the constitution and the root README, when they are read, then each names the seven steps. Closed by: the step-count check TSK-3840 adds.

## What to do

Change `plugins/meow-flow/skills/method/`, `plugins/meow-flow/templates/`, `plugins/meow-flow/agents/`, `/meow-flow:run`, `CLAUDE.md`, `README.md`, `llms.txt` and `plugins/meow-flow/README.md`. The budget check must still pass on `meow-flow`.

## Depends on

- TSK-3810 (not blocking): the prompts name the steps `paw ready` knows, and either can land first.

## Cover

Not yet. The cover step replaces this line with four, `Checks`,
`Failing run`, `Landed in` and `Judgement`, and `paw ready implement` refuses
the task until they are filled.

## Evidence

The class `ShortChainPrompts` in `plugins/meow-flow/tests/test_record.py`
holds seven checks, one or more for each criterion, and each failed at the
pull request's first commit. `meow-author check` reports 0 authoring failures
and the budget check reports `meow-flow` at 818 of 820 characters. The pull
request removes the cover, document and verify step files, the record
reviewer agent and its eight evaluation cases, and the `## Cover` and
`checked-at` of the task and epic templates.

## Left alone

The in-flight worktrees for TSK-2703, TSK-2950, TSK-3350 and TSK-3700 are
postponed by the owner and left as they are.
