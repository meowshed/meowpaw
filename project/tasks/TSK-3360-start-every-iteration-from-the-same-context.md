---
id: TSK-3360
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-1910
closes: [REQ-0880, REQ-0882]
issue:
---

# Start every iteration from the same frozen prompt and preamble, and carry progress in a file

Every call of a run carries the same prompt bytes and the same fixed preamble
in a new session, and the preamble names the run's `progress/progress.md`,
which `--add-dir` makes reachable. Each iteration then begins from the same
stated context, and what the model did before reaches it only through that
file. One task, one branch, one pull request, one review.

## Acceptance criteria

Every check below lives in `plugins/meow-loop/tests/test_loop.py` and counts
what it matched, failing on a count of zero where one was expected (EPC-1910
criterion 13).

1. Given a run of three calls whose stand-in reports a non-zero
   `total_cost_usd` on each call and edits the prompt file in the work tree
   after the first call, when the call log is read, then every
   call's standard input is byte-identical to the prompt as it was at start,
   every call's `--append-system-prompt` value is byte-identical, the run's
   `prompt.md` is byte-identical to each call's standard input, and no argv
   holds `--resume` or `--continue`. The non-zero cost makes a preamble that
   carried the spend differ between calls. Closed by:
   `Context.test_every_call_starts_the_same` (REQ-0880; the "rather than in
   the conversation" half of REQ-0882; EPC-1910 criterion 6, the standard
   input, preamble and session part).
2. Given a run of at least two calls, when every recorded argv and preamble
   are read, then the preamble holds the absolute path of the run's
   `progress/progress.md` and the condition's text, and each argv holds
   `--add-dir` followed by that file's directory and an allow rule for Edit
   and Write of that file. Closed
   by: `Context.test_progress_file_is_named_and_reachable` (REQ-0882,
   EPC-1910 criterion 7).
3. Given a stand-in that appends a line to the progress file each call, when
   the run's directory is read after three calls, then `progress.md` holds
   three lines. Closed by: `Context.test_progress_survives_iterations`
   (REQ-0882). REQ-0882 declares a static check, and criteria 2 and 3 run the
   runner instead, which is stronger: they show the file named, reachable by
   rule and kept between calls, not only the code that names it. Whether a
   real call can write it is unobserved, as Left alone says.
4. Given this change's tree, when `meow-verbs run format lint check test
build` runs, then each passes. Closed by: the kept evidence of that run.

## What to do

Add to the call TSK-3350 makes, as SPC-1201's section "Each call" states.
Read the prompt file once at start and keep its bytes in memory. Write the
run's `prompt.md`, which TSK-3350 already writes, from those bytes and not
from a second read of the file, so the copy and every call carry the same
bytes. Add the allow rule for Edit and Write of the progress file to every
call, as SPC-1201's section "Each call" states. Write the preamble as fixed text naming the progress
file's absolute path and the condition, and saying the runner decides
completion and holds the bounds, with no iteration number and no spend in it.

Raise `meow-loop`'s minor version in `plugin.json`, and its README's
`describes:` with it, because each call gains the preamble and the progress
file.

Write the checks for criteria 1 to 3 first, in a commit of their own, and
see them fail, because the cover step keeps that failing run as the evidence
that the checks can fail (EPC-1910, Coverage). Criterion 4 is outside this
rule, because it runs the verbs over the change and adds no check of its
own.

## Depends on

TSK-3350, because this task changes the call that task makes.

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

Whether a real call under `dontAsk` can write `progress.md` through
`--add-dir`, which ADR-2010 records as unobserved and a stand-in can't show.
The unit's own `--plugin-dir` and the deny rule on `meow-loop`, which
TSK-3390 and TSK-3400 add to the same argv.
