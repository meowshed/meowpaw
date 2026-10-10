---
id: TSK-5292
artifact: task
status: done
revised: 2026-10-10
epic: EPC-2770
closes: [REQ-4406, REQ-4408]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The commit skill states the unit of a pull request

The commit skill's rules B1 and B6 say that one epic or defect is one branch, one
pull request and one review, that an epic which would not be one reviewable
change is split into epics before its work starts, and that an epic or a defect
with no unmerged dependency opens its pull request against the trunk.

## Acceptance criteria

1. Given the commit skill, when rule B1 is read, then it names an epic or a
   defect as the unit of a branch, a pull request and a review. Closed by: a test
   in `plugins/meow-scm/tests`.
2. Given the commit skill, when rule B6 is read, then it asks for the epic to be
   split before work starts and not the pull request. Closed by: a test in the
   same directory.

## What to do

Change rules B1 and B6 of `plugins/meow-scm/skills/commit/SKILL.md`, keep its
character budget, and update its mirrored package copy and the tests that
assert its wording.

## Depends on

- TSK-5291 (not blocking): the two texts agree, and either task can write
  first.

## Evidence

Pull request 880. The tests are in `plugins/meow-scm/tests/test_scm.py`, class
`CommitSkill`:

- Criterion 1: `test_b1_names_the_epic_or_the_defect_as_the_unit`.
- Criterion 2: `test_b6_splits_the_epic_before_the_work_starts`.

## Left alone

The method unit's text, which TSK-5291 changes.
