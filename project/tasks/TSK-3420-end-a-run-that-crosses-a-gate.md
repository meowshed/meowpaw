---
id: TSK-3420
artifact: task
status: approved
revised: 2026-09-30
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

**Amended by ADR-2300.** Criterion 2 drops the `verify` run and `checked-at`, which ADR-2300 removed. Its verbs criterion is closed by the pull request's gate, since no run output is kept, and it names the checks unit `meow-checks`.

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
   then it doesn't. Given an `implement`
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
7. Given this change's tree, when `meow-checks run format lint check test
build` runs, then each passes. Closed by: each verb's outcome in the task's pull request.

## What to do

Add step 5's `crossed` half after each call, and the comparison after each
evaluation that changed the tree, as SPC-1201's sections "The loop" and
"Keeping to one step" state, with `crossed` in the endings table. Have the
record code expose the frozen comparison with its exemptions switchable, and
each kind's allowance after approval, as ADR-2020's consequences name. Take
none of the comparison's exemptions: a
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

Criteria 1 to 6 are closed by the 21 `Crossed` checks in
`plugins/meow-loop/tests/test_loop.py`. In commit 29fb51fb, eleven of the
first twelve failed, ending `ceiling` or `finished` where `crossed` was
expected, and `test_defect_allowances` failed in its second half only. The
twelfth, `test_drafts_and_task_evidence_cross_nothing`, passed there, because
it guards against a comparison that crosses too much. The review then added
nine checks in d8a58083. Six cases of them failed first: a copied approved
record, an approved record overwritten by a draft with a held identifier, two
records sharing an identifier at start, and three epic changes outside the
marks. The others passed on the earlier code and pin a rule against a wrong
change, such as moving `crossed` ahead of `tampered`. All 78 checks of the
unit pass on this change, by `python3 -m unittest
plugins/meow-loop/tests/test_loop.py`, which exits 0. Criterion 7 is closed
by the five verbs' outcomes in this task's pull request, #796, since no run
output is kept.

The comparison lives in `crossings` in `crates/meow/src/record.rs`, and the
runner calls it after a call and after each verb of an evaluation that changed
the tree. A document is matched to its held copy by path and identifier
first, because identifiers can repeat. The verb result carries the tree
before and after again, which TSK-3410 had dropped as unread.

A record the program can't read becomes empty text with no status. One
unreadable at start is then never guarded, and one a call makes unreadable
crosses. SPC-1201 names no failure state for it, so it belongs on the list
BUG-1390 holds for the spec step. A layout that can't be read after start
stops the run with exit status 3 and no ending, which BUG-1390 already
records.

## Left alone

The `off-step` half of step 5, which TSK-3440 adds after this check. The
hook's status rule, which TSK-3430 adds. `paw check frozen`'s own behaviour,
which keeps its exemptions, because a person's approval and withdrawal are
acts the method allows outside a run.
