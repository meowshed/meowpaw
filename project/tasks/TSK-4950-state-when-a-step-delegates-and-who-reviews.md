---
id: TSK-4950
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2530
closes: [REQ-0818, REQ-0824, REQ-0826, REQ-0828, REQ-2980]
issue: 972
projected: e3b365aa4e42
tracked: d23afd8f46d3
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# State when a step delegates, how it dispatches and who reviews

The implement step's file and the method skill state the rules SPC-1030
gives under "Delegation" and SPC-1090 gives under "Delegated work": delegate
only to keep a context clean or to run independent tracks, dispatch with
`paw brief` and `isolation: worktree`, review with a fresh agent, resolve a
disagreement in a third, and name the task and its brief in the pull
request. One task, one branch, one pull request, one review: the tests
first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given `plugins/meow-flow/skills/method/steps/implement.md`, when a test
   reads it, then it names the two reasons to delegate and forbids delegating
   because a task is large (REQ-0826, REQ-0828). Closed by: a test under
   `plugins/meow-flow/tests/` naming both requirements, seen failing first.
2. Given the same file, when the test reads it, then a parallel dispatch
   declares `isolation: worktree` and the brief is `paw brief <task>`'s
   output (REQ-2980). Closed by: the same test.
3. Given a fixture session that dispatches a review of delegated work, when
   the fixture reads the dispatch, then it is a fresh agent and not a fork,
   and a disagreement goes to a third fresh agent given both positions and
   the brief (REQ-0818, REQ-0824). Closed by: a hand-run case under
   `plugins/meow-flow/evals/`, run on Sonnet 5 and Opus 5.5, which rests on
   judgement where the dispatch can't be read by a program.
4. Given the implement step's file, when the test reads it, then a delegated
   pull request names the task and `paw brief <task>`, and the file names no
   agent, model or vendor to put in a pull request. Closed by: the same test,
   and `meow-scm check-message` on the step's example.

## What to do

Change `steps/implement.md` and, where every step needs it, the method
skill's `SKILL.md`, held to SPC-1030 and the unit's `budget.toml`. Keep
SPC-1090's review section true: the review step already dispatches a fresh
agent for the session's own change, so this task extends the rule to
delegated work and doesn't repeat it.

## Depends on

- TSK-4945 (blocking): the step names `paw brief`, which has to exist before
  the step tells anyone to run it.

## Evidence

Criteria 1, 2 and 4 are closed by `plugins/meow-flow/tests/test_delegation.py`:
`test_two_reasons_to_delegate_and_never_because_a_task_is_large` names
REQ-0826 and REQ-0828,
`test_a_parallel_dispatch_declares_a_worktree_and_carries_the_brief` names
REQ-2980, and `test_a_delegated_pull_request_names_the_task_and_the_brief_and_no_agent`
with `test_the_steps_example_passes_the_message_check` close criterion 4, the
second running `meow-scm check-message` on the step's example. Each was seen
failing before the step changed, and `test_the_pi_step_says_the_same` holds
the Pi tree's copy to it.

Criterion 3 rests on judgement, because a program can't read which agent a
session chooses to dispatch. A case was run by hand once on `sonnet` and once
on `opus`: 4 of 4 runs as wanted, each review a fresh dispatch and never a
fork, and each disagreement sent to a fresh agent whose prompt held both
positions and the brief. One run per case is a smoke check and not a
measurement, and the case isn't kept, because ADR-2980 removed the case sets
after this task was approved and review holds the step instead.

Every stage passed in pull request #PR.

## Left alone

Which steps delegate by default, which ADR-2560 leaves open, and the review
step's own rules, which SPC-1090 states and this task cites.
