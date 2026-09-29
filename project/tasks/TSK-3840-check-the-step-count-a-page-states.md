---
id: TSK-3840
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-2200
closes: [REQ-3632]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Make the documentation check report a page stating the wrong step count

`tools/check_docs.py` reports a living page that states a number of the method's steps other than the number `method/SKILL.md` names. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given a fixture page saying "the same ten steps" while the skill names seven, when `python3 tools/check_docs.py` runs, then it exits 1 naming the page and the line. Closed by: a test in `tools/test_check_docs.py`.
2. Given the repository after TSK-3820, when the check runs, then it reports nothing. Closed by: the `test` verb.

## What to do

Change `tools/check_docs.py` and its test. Read the count from `method/SKILL.md`, never a constant.

## Depends on

- TSK-3820 (blocking): the pages say ten until it lands, so the check would fail the gate.

## Cover

Not yet. The cover step replaces this line with four, `Checks`,
`Failing run`, `Landed in` and `Judgement`, and `paw ready implement` refuses
the task until they are filled.

## Evidence

Not yet.

## Left alone

The in-flight worktrees for TSK-2703, TSK-2950, TSK-3350 and TSK-3700 are
postponed by the owner and left as they are.
