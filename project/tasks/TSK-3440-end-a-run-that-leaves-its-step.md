---
id: TSK-3440
artifact: task
status: approved
revised: 2026-09-30
epic: EPC-1920
closes: [REQ-0888]
issue: 740
projected: 9a5324d8e467
---

# End a run `off-step` when a call writes another step's files or leaves its input unready

After the `crossed` check, the runner ends the run `off-step`, naming each
record or path, when a call wrote a record of a kind its step doesn't write,
changed a path outside the record root in a step that doesn't allow it, or left
an input failing the start test. REQ-0888 closes here, citing the checks of TSK-3410, TSK-3420
and TSK-3430. One task, one branch, one pull request, one review.

**Amended by ADR-2300.** Criterion 2 drops `checked-at` and the Cover lines, which ADR-2300 removed, and tests a dependency left undone, which fails the start test without changing an approved record's frozen part. Its verbs criterion is closed by the pull request's gate, since no run output is kept, and it names the checks unit `meow-checks`.

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
2. Given an `implement` run of a task with a blocking dependency marked done,
   when a stand-in clears that dependency's mark in the approved epic's Tasks
   and changes nothing else, then the input fails the start test and the run
   ends `off-step` naming the input task. Closed by:
   `OffStep.test_implement_run_limits` (REQ-0888, in place of EPC-1920
   criterion 11).
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
7. Given REQ-0888, when this task closes it, then its evidence cites the
   checks of TSK-3410's criteria 6 and 9, TSK-3420's criteria 1 to 4 and
   TSK-3430's criterion 1 at their merged revisions. Judgement, because
   whether one requirement is met by five tasks' checks is a reading of the
   evidence together, which no single check performs; the reviewer reads
   that each cited check passed in the pull request that merged it.
8. Given this change's tree, when `meow-checks run format lint check test
build` runs, then each passes. Closed by: each verb's outcome in the task's pull request.

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

## Evidence

`python3 -m unittest plugins/meow-loop/tests/test_loop.py` exits 0 on this
change, reporting `Ran 94 tests` and `OK`. Seven checks in the `OffStep`
class close criteria 1 to 6: `test_design_run_kinds`,
`test_implement_run_limits`, `test_unidentified_tree_in_a_record_step`,
`test_verb_rewrites_are_not_the_calls`, `test_always_allowed`,
`test_crossed_first` and `test_each_kind_has_its_step`. Four of them failed
first in the checks' own commit, ending `ceiling` or `finished` where
`off-step` was expected: the design kinds, the implement limits, the
unidentified tree and each kind's step. The other three pin rules that held
already, such as `crossed` coming first. Criterion 8 is closed by the five
verbs' outcomes in this task's pull request, since no run output is kept.

Criterion 7 rests on judgement, because whether one requirement is met by five
tasks' checks is a reading of the evidence together, which no single check
performs. REQ-0888 is met by these checks, each at the pull request that
merged it. In #795, `Step.test_step_usage_errors`,
`Step.test_step_unresolved_states`, `Step.test_run_toml_holds_the_step` and
`Step.test_preamble_names_the_step` cover the step, its inputs and the
preamble that names them. In #796, `Crossed.test_decided_status`,
`Crossed.test_withdrawal`, `Crossed.test_authority_line`,
`Crossed.test_removed`, `Crossed.test_renamed`,
`Crossed.test_epic_allowances`, `Crossed.test_defect_allowances`,
`Crossed.test_crossed_with_unidentified_tree` and
`Crossed.test_live_only_in_a_living_kind` cover a decided status and a change
to an approved record. In #797, `Hook.test_status_rule` covers the hook's
refusal. The checks of this task cover the rest. Each cited check passed in
its pull request, whose gate ran before the merge.

The comparison lives in `off_step` in `crates/meow/src/record.rs`, and the
runner calls it after `crossed` and lists the changed paths in `changed_paths`
in `crates/meow/src/runloop.rs`. A step that writes only records may not
change the work tree's root, so the stand-in `claude` edits a file under the
record root in those steps, and two spec-run checks start with `done.flag` in
place and no longer create it in a call.

## Left alone

The user-facing pages an `implement` run may change, because the
harness names no language and can't tell a page from code (ADR-2020). Binding
a run to the step's own artifact paths, which ADR-2020 names as the change a
reversal would bring.
