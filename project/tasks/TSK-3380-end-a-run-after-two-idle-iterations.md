---
id: TSK-3380
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-1910
closes: [REQ-0886]
issue: 728
projected: 471a85de25a3
---

# End a run after two iterations in a row that change nothing

Two iterations in a row that change nothing end the run `idle`, where
"changes nothing" is as SPC-1201's section "The loop" defines it. Every
fixture below uses a verb that never passes, so no run ends `finished`. One task, one branch, one pull
request, one review.

## Acceptance criteria

Every check below lives in `plugins/meow-loop/tests/test_loop.py` and counts
what it matched, failing on a count of zero where one was expected (EPC-1910
criterion 13).

1. Given a stand-in that changes nothing and `--iterations 5`, when the run
   ends, then the call log holds exactly two calls, `run.toml` records
   `idle`, the runner exits 1, and each `log.jsonl` line records that
   `progress.md` didn't change. Closed by: `Idle.test_two_idle_iterations_end_the_run` (REQ-0886, EPC-1910
   criterion 8).
2. Given a stand-in that writes only `progress.md` on each call and
   `--iterations 4`, when the run ends, then the call log holds four calls
   and the run ends `ceiling` with exit 1, and each `log.jsonl` line records
   that `progress.md` changed. Closed by:
   `Idle.test_progress_alone_is_a_change` (REQ-0886, EPC-1910 criterion 8).
3. Given a stand-in that changes nothing on its first call, a tracked file on
   its second and nothing on its third and fourth, and `--iterations 6`, when
   the run ends, then it ends `idle` after the fourth call. Closed by:
   `Idle.test_idle_iterations_must_be_consecutive` (REQ-0886, EPC-1910
   criterion 8).
4. Given a fixture with a dirty submodule, so the tree id is `none` on every
   call, a stand-in that changes nothing else, and `--iterations 3`, when the
   run ends, then it ends `ceiling` after three calls and not `idle` after
   two, and each `log.jsonl` line is marked `unidentified`. Closed by:
   `Idle.test_unidentified_tree_is_a_change` (evidence for SPC-1201's section
   "The loop"; closes no requirement).
5. Given this change's tree, when `meow-verbs run format lint check test
build` runs, then each passes. Closed by: the kept evidence of that run.

## What to do

Add step 6 after each call, as SPC-1201's section "The loop" states, reading
the tree id TSK-3350 records and hashing the progress file before and after
each call. Record in each `log.jsonl` line whether `progress.md` changed and
the `unidentified` marker, the two fields TSK-3350's criterion 7 leaves to
this task.

Raise `meow-loop`'s minor version in `plugin.json`, and its README's
`describes:` with it, because a run gains an ending.

Write the checks for criteria 1 to 4 first, in a commit of their own, and
see them fail, because the cover step keeps that failing run as the evidence
that the checks can fail (EPC-1910, Coverage).

## Depends on

TSK-3350, because this task reads the tree id and the progress file that
task records.

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

A run that writes only `progress.md` each call and never changes the tree,
which the idle rule doesn't end and the ceiling and the budget bound, as
ADR-2010's premortem says.
