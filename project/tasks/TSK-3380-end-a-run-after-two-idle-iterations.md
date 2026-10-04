---
id: TSK-3380
artifact: task
status: done
revised: 2026-09-30
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

**Amended by ADR-2300.** Its verbs criterion is closed by the pull request's gate, since no run output is kept, and it names the checks unit `meow-checks`.

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
5. Given this change's tree, when `meow-checks run format lint check test
build` runs, then each passes. Closed by: each verb's outcome in the task's pull request.

## What to do

Add step 6 after each call, as SPC-1201's section "The loop" states, reading
the tree id TSK-3350 records and hashing the progress file before and after
each call. Record in each `log.jsonl` line whether `progress.md` changed and
the `unidentified` marker, the two fields TSK-3350's criterion 7 leaves to
this task.

Raise `meow-loop`'s minor version in `plugin.json`, and its README's
`describes:` with it, because a run gains an ending.

Write the checks for criteria 1 to 4 first, in a commit of their own, and
see them fail, because that commit is the evidence that the checks can fail (EPC-1910, Coverage).

## Depends on

TSK-3350, because this task reads the tree id and the progress file that
task records.

## Evidence

`run` in `crates/meow/src/runloop.rs` hashes `progress/progress.md` before
and after each call and reads the tree id on both sides. An iteration changes
nothing when both tree ids are identified and equal and the hash is the same.
After the condition, two such iterations in a row end the run `idle`. Each
`log.jsonl` line gains `progress_changed` and `unidentified`.

Criteria 1 to 4 are closed by the checks they name, in
`plugins/meow-loop/tests/test_loop.py`:

1. `Idle.test_two_idle_iterations_end_the_run`
2. `Idle.test_progress_alone_is_a_change`
3. `Idle.test_idle_iterations_must_be_consecutive`
4. `Idle.test_unidentified_tree_is_a_change`

No criterion rests on judgement. The four checks failed first, in the commit
that holds them alone, where the `test` verb exited 1. That commit also
changes `Unchanged.test_an_unchanged_tree_skips_the_verbs`, whose stand-in
changes nothing and so now ends `idle` after two of three calls, and it failed
there too. Criterion 5 is closed by the pull request, where `format`, `lint`,
`check`, `test` and `build` each pass on the change's tree.

I made three choices the task leaves open. A progress file the runner can't
read counts as changed, as an unidentified tree does, so neither ends a run
`idle`. An absent progress file is a state of its own, so a call that removes
the file changes it and later calls that leave it absent can end the run
`idle`; `Idle.test_a_removed_progress_file_can_go_idle` checks it. `unidentified` is true where either tree id, before or after the
call, is `none`.

`meow-loop` goes to 0.4.0, and its README states the ending and the two
fields.

## Left alone

A run that writes only `progress.md` each call and never changes the tree,
which the idle rule doesn't end and the ceiling and the budget bound, as
ADR-2010's premortem says.
