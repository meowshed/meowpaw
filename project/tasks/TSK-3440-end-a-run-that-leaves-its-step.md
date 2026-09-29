---
id: TSK-3440
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-1920
closes: [REQ-0888]
issue:
---

# End a run `off-step` when a call writes another step's files or leaves its input unready

After the `crossed` check, the runner ends the run `off-step`, naming each
record or path, when a call wrote a record of a kind its step doesn't write,
changed a path outside the record root in a step that doesn't allow it, left
an input failing the start test, or set an epic's `checked-at` in an
`implement` run. REQ-0888 closes here, citing the evidence TSK-3410, TSK-3420
and TSK-3430 kept. One task, one branch, one pull request, one review.

## Acceptance criteria

Every check below lives in `plugins/meow-loop/tests/test_loop.py`, builds its
small record in a scratch git repository, and counts what it matched, failing
on a count of zero where one was expected (EPC-1920 criterion 17).

1. Given a `design` run, when a stand-in writes a draft decision addressing
   the input and a specification, then the run ends `off-step` naming the
   specification; when one writes a file outside the record root, then it
   ends `off-step` naming the file; when one writes only the decision while
   the verb passes, then it ends `finished`. Closed by:
   `OffStep.test_design_run_kinds` (REQ-0888, EPC-1920 criterion 8).
2. Given an `implement` run, when a stand-in sets the epic's `checked-at`,
   then the run ends `off-step` naming the epic; when one empties the input
   task's `## Cover` lines, then it ends `off-step` naming the task. Closed
   by: `OffStep.test_implement_run_limits` (REQ-0888, EPC-1920 criterion 11).
3. Given a `design` run with a dirty submodule, when a stand-in writes the
   decision, then the run ends `off-step` and `log.jsonl` records the tree as
   `unidentified`. Closed by: `OffStep.test_unidentified_tree_in_a_record_step`
   (REQ-0888, EPC-1920 criterion 12, the `off-step` half).
4. Given a `design` run whose verb is TSK-3410's formatter, set to rewrite an
   approved requirement and a file outside the record root on its first run,
   when a stand-in writes only the decision, then the run ends `finished`,
   and neither `crossed` nor `off-step`. Closed by:
   `OffStep.test_verb_rewrites_are_not_the_calls` (REQ-0888, EPC-1920
   criterion 15).
5. Given any step, when a stand-in writes a draft defect, a draft insight or
   an index under the record root, then the run doesn't end `off-step`.
   Closed by: `OffStep.test_always_allowed`.
6. Given a call that both approves a draft and writes another step's record,
   when the run ends, then it ends `crossed`. Closed by:
   `OffStep.test_crossed_first`.
7. Given REQ-0888, when this task closes it, then its evidence cites the kept
   runs of TSK-3410's criteria 6 and 9, TSK-3420's criteria 1 to 4 and
   TSK-3430's criterion 1 at their merged revisions. Judgement, because
   whether one requirement is met by five tasks' checks is a reading of the
   evidence together, which no single check performs; the reviewer reads
   that each cited run passed at the revision it names.
8. Given this change's tree, when `meow-verbs run format lint check test
build` runs, then each passes. Closed by: the kept evidence of that run.

## What to do

Add the `off-step` half of step 5 after each call, after `crossed`, as
SPC-1201's section "Keeping to one step" states, with `off-step` in the
endings table. List the changed paths with `git diff-tree -r --name-only`
between the tree id read immediately before the call, after the runner's own
evaluation, and the tree id after it. Where either id is unidentified, end a
run of a step that writes only records `off-step`, because the runner can't
list the paths.

Raise `meow-loop`'s minor version in `plugin.json`, and its README's
`describes:` with it, because a run gains an ending.

Write the checks first, in a commit of their own, and see them fail on the
tree TSK-3420 and TSK-3430 leave.

## Depends on

- TSK-3420 (blocking): `crossed` is checked before `off-step` in the same
  step after the call.
- TSK-3430 (blocking): REQ-0888 closes here, so every guard it names must
  have landed first.

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

The user-facing pages a `cover` or `implement` run may change, because the
harness names no language and can't tell a page from code (ADR-2020). Binding
a run to the step's own artifact paths, which ADR-2020 names as the change a
reversal would bring.
