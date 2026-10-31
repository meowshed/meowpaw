---
id: TSK-5360
artifact: task
status: done
revised: 2026-10-10
epic: EPC-2330
closes: []
issue: 1090
projected: a8aa87966bdd
tracked: aed8635e3c48
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Carry an epic's tasks on its one branch, and merge at its last task

The prompts that drive the chain take one task to one pull request, so a run
that works an epic with three tasks opens, reviews and merges three pull
requests where REQ-4400, REQ-4410 and REQ-4414 ask for one. This task makes
the run skill, the implement step, the review step and the `task` record type
say what the requirements say. It restores them and closes none, because
ADR-2860 addresses them and TSK-5291 closed them: the tasks of an epic are groups of commits on
the epic's one branch, and the pull request merges when the epic's last task is
done. One task is a group of commits in its epic's pull request: the tests
first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given the run skill's steps for a run, when a test reads them, then they
   name the epic's pull request and not each task's, tell the run to continue
   with the epic's next task on the same branch while one is ready, and merge
   only where `paw status` shows the epic closed (REQ-4400, REQ-4414). Closed
   by: a test in `plugins/meow-flow/tests/test_run_skill.py` naming both
   requirements, seen failing first.
2. Given the implement step, when a test reads its steps, then the step that
   marks a task goes on to the epic's next ready task on the branch and stops
   at the epic's pull request, where no task of the epic is left (REQ-4410,
   REQ-4414). Closed by: a test in the same file naming both.
3. Given the review step and the `task` record type, when a test reads their
   opening, then each says a task's changes are reviewed and merged inside its
   epic's pull request, and neither says a task has a branch, a pull request or
   a review of its own (REQ-4400). Closed by: a test in the same file naming
   REQ-4400, and for the type a test in `plugins/meow-prose/tests/`.

## What to do

Change the sentences that attach a branch, a pull request or a merge to a
task, in `plugins/meow-flow/skills/run/SKILL.md`,
`plugins/meow-flow/skills/method/steps/implement.md`,
`plugins/meow-flow/skills/method/steps/review.md` and
`plugins/meow-prose/skills/writing/types/record/task.md`, and no other
sentence. A defect's tasks and a task that realises a decision with no epic
keep their own pull request, as REQ-4402 and REQ-4404 state.

Leave the frozen task records that say "One task, one branch, one pull
request": an approved record isn't reworded, and the template already says what
this task makes the prompts say.

## Depends on

Nothing.

## Evidence

The tests came first, in a commit of their own, where three tests in
`plugins/meow-flow/tests/test_run_skill.py` and one in
`plugins/meow-prose/tests/test_task_type.py` failed for the missing wording.
`test_a_run_opens_one_pull_request_for_an_epic_and_merges_at_its_last_task`
closes criterion 1 (REQ-4400, REQ-4414),
`test_the_implement_step_goes_on_to_the_epics_next_task` closes criterion 2
(REQ-4410, REQ-4414), and
`test_the_review_step_reads_an_epics_pull_request` with `TaskType` closes
criterion 3 (REQ-4400). `test_review_is_a_code_review_in_the_pull_request` in
`test_record.py` named the old wording and now names the epic's pull request.
`mise run all` passed with exit status 0.

A review by a separate agent found the merge condition naming only an epic, a
retired section's reason, the method skill's description, the task type and the
review step still attaching a pull request to one task, and tests that would
pass on a near miss. Each was corrected in the same pull request, and the tests
came first again: `test_no_prompt_gives_a_task_a_branch_a_pull_request_or_a_review_of_its_own`
holds the shipped prompts, `lib/layout.toml` and the README to the wording, and
`test_a_defect_or_a_task_that_realises_a_decision_keeps_its_own_pull_request`
holds the exception REQ-4402 and REQ-4404 state.

## Left alone

The method's other steps, `paw status`'s `next:` lines, which name the task a
person works next and not a pull request, and the records TSK-4330 to TSK-4350
change.
