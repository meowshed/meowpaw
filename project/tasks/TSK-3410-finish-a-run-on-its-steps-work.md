---
id: TSK-3410
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-1920
closes: [REQ-0884]
issue: 737
projected: 9c9bdfa1e4da
---

# Bind a run to one step, and finish it only when the step's work is done and the verbs pass at one tree

`meow-loop start` takes `--step` and `--inputs`, refuses a run without them or
over an input that isn't ready, and holds a copy of the record from after its
first evaluation. The condition becomes two terms at one tree: the step's
test from SPC-1201's table, and the held verb commands, with one repeat where
a verb rewrote the tree. The runner reads no pass from the ledger and nothing
the model printed. One task, one branch, one pull request, one review.

## Acceptance criteria

Every check below lives in `plugins/meow-loop/tests/test_loop.py`, builds its
small record in a scratch git repository, and counts what it matched, failing
on a count of zero where one was expected (EPC-1920 criterion 17).

1. Given a stand-in whose result text says "DONE, all tests pass" while the
   verb's command exits 1, and `--iterations 3`, when the run ends, then it
   ends `ceiling` after three calls. Closed by: `Step.test_phrase_is_not_done`
   (REQ-0884, EPC-1920 criterion 1).
2. Given a stand-in that appends a passing ledger line for the verb at the
   current tree while the verb's command exits 1, when the run ends, then it
   doesn't end `finished`. Closed by: `Step.test_ledger_line_is_not_done`
   (REQ-0884, EPC-1920 criterion 2).
3. Given a verb whose command reformats a tracked file on its first run and
   exits 0, when the run evaluates, then it ends `finished` after the repeated
   evaluation; given a verb that changes the tree on every run, then it never
   ends `finished`. Closed by: `Step.test_repeat_once_after_a_write` and
   `Step.test_restless_verb_never_finishes` (REQ-0884, EPC-1920 criterion 3).
4. Given a dirty submodule, when the run evaluates, then the condition never
   holds and `log.jsonl` records the tree as `unidentified`. Closed by:
   `Step.test_dirty_submodule_holds_nothing` (REQ-0884, EPC-1920 criterion
   4).
5. Given an `implement` run, when a stand-in marks the input task `~`, then
   the run doesn't end `finished`; when one marks it `x` with text in its
   `## Evidence` while the verb passes, then it ends `finished` after that
   call. Closed by: `Step.test_dropped_is_not_done` and
   `Step.test_marked_done_finishes` (REQ-0884, EPC-1920 criterion 5).
6. Given `start` without `--step`, with `--step document`, `--step review` or
   an unknown step, with `--inputs` on `research`, or without it on `design`,
   when it runs, then it exits 2 and leaves no run directory. Given `start`
   over a draft requirement, or with the record root ignored by git, missing,
   or outside the work tree, then it exits 3, prints the reason SPC-1201's
   "Failure paths" gives and leaves no run directory. Given a started run,
   then `run.toml` holds `step` as a string and `inputs` as a list. Closed by:
   `Step.test_step_usage_errors`, `Step.test_step_unresolved_states` and
   `Step.test_run_toml_holds_the_step` (EPC-1920 criterion 6).
7. Given a `spec` run, when a stand-in writes a new specification with status
   `live` stating each requirement the input decision addresses while the
   verb passes, then the run ends `finished`. Closed by:
   `Step.test_spec_run_finishes` (EPC-1920 criterion 13, the `finished`
   half).
8. Given a `design` run over a requirement an approved decision already
   addresses, when it starts, then it makes a call; when a stand-in writes a
   new draft decision addressing the requirement that names the decision it
   amends and changes nothing in it, then it ends `finished`. Closed by:
   `Step.test_amending_design_run_finishes` (REQ-0884, EPC-1920 criterion
   14).
9. Given a run of at least two calls, when the recorded preambles are read,
   then each names the step and its inputs and all are byte identical. Closed
   by: `Step.test_preamble_names_the_step` (EPC-1920 criterion 16).
10. Given a `cover`, `implement` or `verify` run whose work is already done
    and whose verbs pass, when it starts, then it ends `finished` with no
    call. Closed by: `Step.test_done_work_makes_no_call`.
11. Given this change's tree, when `meow-verbs run format lint check test
build` runs, then each passes. Closed by: the kept evidence of that run.

## What to do

Add `--step` and `--inputs` to `start` as SPC-1201's section "The terms"
states, with the usage errors and the unresolved states its "Failure paths"
lists, and write both into `run.toml`. Compile the `record` feature's code
into the `loop` feature, and have the record code expose the test
`paw ready` applies, the step's test for each of the eight steps in
SPC-1201's table, and a copy of the record the runner can hold in memory.
Apply the readiness test through that code, and never run `paw` as a program,
because the `standalone` gate refuses it and `paw ready` exits 1 for a
missing record as for an unready input (RES-0301).

Take the copy held at start after the evaluation before the first call.
Evaluate the condition as SPC-1201's section "Evaluating the condition"
states: tree id, the step's test, each held verb command, tree id again, and
one repeat where both ids are identified and differ. Record each verb's
result in the ledger through the `verbs` code, and read nothing back from it.
Extend the preamble with the step, its inputs, what the step may write, the
three things that end a run early and the instruction to record a defect as a
draft, as the section "Each call" states. Update the skill's `start` command
to name `--step` and `--inputs`.

Raise `meow-loop`'s minor version in `plugin.json`, and its README's
`describes:` with it, because `start` gains a required flag and the
condition gains a term.

Write the checks first, in a commit of their own, and see them fail on the
tree EPC-1910 leaves, because the cover step keeps that failing run as the
evidence that the checks can fail (EPC-1920, Coverage).

## Depends on

- TSK-3360 (blocking): the preamble this task extends.
- TSK-3370 (blocking): the condition and the meter checks this task changes.
- TSK-3390 (blocking): the held verb commands and the hash checks the
  condition runs after.

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

The comparison after each call and the endings `crossed` and `off-step`,
which TSK-3420 and TSK-3440 add; this task holds the copy they compare
against and nothing reads it yet. The hook, which TSK-3430 changes.
`paw ready`'s exit status for a missing record, which ADR-2020 leaves
unsettled. `meow-flow`'s version, because exposing the record code to another
feature changes nothing `paw` does.
