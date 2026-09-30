---
id: TSK-3420
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-1920
closes: []
issue: 738
projected: 2fdad6246ef5
---

# End a run `crossed` when a call or an evaluation decides a status or changes an approved record

After each call whose tree changed or couldn't be identified, and after each
of its own evaluations that changed the tree, the runner compares the record
with the copy held at start. A decided status, an approved record removed,
renamed or changed outside what the step may change in it, ends the run
`crossed`, naming each record. This task closes no requirement, because
REQ-0888 closes in TSK-3440 (EPC-1920, Coverage). One task, one branch, one
pull request, one review.

## Acceptance criteria

Every check below lives in `plugins/meow-loop/tests/test_loop.py`, builds its
small record in a scratch git repository, and counts what it matched, failing
on a count of zero where one was expected (EPC-1920 criterion 17).

1. Given a `design` run, when a stand-in sets a draft decision's status to
   `approved`, then the run ends `crossed` after that call and the last line
   names the decision. The same holds when a stand-in sets an approved
   requirement to `withdrawn`, appends to an approved requirement a line
   naming an amendment in the form the frozen check accepts, deletes an
   approved requirement, or renames one. Closed by:
   `Crossed.test_decided_status`, `Crossed.test_withdrawal`,
   `Crossed.test_authority_line`, `Crossed.test_removed` and
   `Crossed.test_renamed` (EPC-1920 criterion 7).
2. Given an `implement` run, when a stand-in rewords an acceptance criterion
   of the approved epic, then the run ends `crossed` naming the epic; when
   one marks the input task `x` in that epic and changes nothing else there,
   then it doesn't. Given a `verify` run, when a stand-in rewords an
   acceptance criterion, then it ends `crossed`; when one writes
   `## Verified` and sets `checked-at`, then it doesn't. Given an `implement`
   run of a task an approved defect authorises, when a stand-in marks the
   task `x` in the defect and changes nothing else, then the run doesn't end
   `crossed`; when one rewords the defect's reproduction, then it does.
   Closed by: `Crossed.test_epic_allowances` and
   `Crossed.test_defect_allowances` (EPC-1920 criterion 10).
3. Given a `design` run with a dirty submodule, when a stand-in sets a draft
   decision to `approved`, then the run ends `crossed`. Closed by:
   `Crossed.test_crossed_with_unidentified_tree` (EPC-1920 criterion 12, the
   `crossed` half).
4. Given a `spec` run, when a stand-in sets a draft requirement's status to
   `live`, then the run ends `crossed`; when it writes a new specification
   with status `live`, then it doesn't. Closed by:
   `Crossed.test_live_only_in_a_living_kind` (EPC-1920 criterion 13, the
   `crossed` half).
5. Given a verb whose command sets an approved requirement's status to
   `withdrawn` on its second run and not its first, when the evaluation after
   a call runs it, then the run ends `crossed`, naming the evaluation and the
   verb and not a call. Closed by: `Crossed.test_evaluation_crosses`.
6. Given a call that both approves a draft and exits with the verbs passing,
   when the run ends, then it ends `crossed` and not `finished`. Closed by:
   `Crossed.test_crossed_before_finished`.
7. Given this change's tree, when `meow-verbs run format lint check test
build` runs, then each passes. Closed by: the kept evidence of that run.

## What to do

Add step 5's `crossed` half after each call, and the comparison after each
evaluation that changed the tree, as SPC-1201's sections "The loop" and
"Keeping to one step" state, with `crossed` in the endings table. Have the
record code expose the frozen comparison with its exemptions switchable, and
each kind's allowance after approval, as ADR-2020's consequences name. Take
none of the comparison's exemptions: an epic whose `checked-at` is empty, a
status now `withdrawn` or `superseded`, and a line naming an authority each
cross. Skip the comparison only where the tree ids before and after the call
are both identified and equal.

Raise `meow-loop`'s minor version in `plugin.json`, and its README's
`describes:` with it, because a run gains an ending.

Write the checks first, in a commit of their own, and see them fail on
TSK-3410's tree.

## Depends on

- TSK-3410 (blocking): the step, the record code and the copy held at start
  that this task compares against.

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

The `off-step` half of step 5, which TSK-3440 adds after this check. The
hook's status rule, which TSK-3430 adds. `paw check frozen`'s own behaviour,
which keeps its exemptions, because a person's approval and withdrawal are
acts the method allows outside a run.
