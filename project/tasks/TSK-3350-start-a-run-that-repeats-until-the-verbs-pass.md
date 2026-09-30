---
id: TSK-3350
artifact: task
status: approved
revised: 2026-09-30
epic: EPC-1910
closes: [REQ-0872]
issue: 725
projected: 00ea37d68251
---

# Add `meow-loop start`, which repeats a call until the verbs pass or the ceiling ends the run

`meow-loop start` refuses to begin without a condition, a ceiling and a
budget, keeps a run's files under the state directory, runs one `claude -p`
call per iteration, holds the ceiling in its own process, and ends the run
`finished` when the named verbs pass. After this task a person can run a loop
bounded by its ceiling, and the budget, the idle rule, the hash check and the
guards against a model start arrive with the tasks after it. This task closes
REQ-0872 alone. REQ-0870 and REQ-0876 each name a budget as well as a
condition or a ceiling, so TSK-3370 closes both once the runner holds the
budget, citing criteria 1 and 3 below for their other halves. One task, one
branch, one pull request, one review.

**Amended by ADR-2300.** Its verbs criterion is closed by the pull request's gate, since no run output is kept, and it names the checks unit `meow-checks`.

## Acceptance criteria

Every check below lives in `plugins/meow-loop/tests/test_loop.py`, runs the
built unit in a fixture git repository in a temporary directory with a
stand-in `claude` first on the path and `CLAUDECODE` removed from the
environment, and counts what it matched, failing on a count of zero where one
was expected (EPC-1910 criterion 13).

1. Given a stand-in that makes the fixture's `test` verb pass on its second
   call, when `start --until verbs=test` runs, then the stand-in's call log
   holds exactly two calls, `run.toml` records `finished` and the runner
   exits 0; given a verb that already passes, then the call log is empty and
   the run ends `finished` with exit 0. Closed by: `Condition.test_finished_after_two`
   and `Condition.test_finished_with_no_call` (the condition half of
   REQ-0870, which TSK-3370 closes; EPC-1910 criterion 1).
2. Given `start` without `--until`, without `--iterations`, without
   `--budget-usd`, without `--permission-mode`, with `--iterations 0`, with `--budget-usd 0`, and with
   `--permission-mode acceptEdits` and `bypassPermissions`, when each runs,
   then it exits 2 and no run directory exists under the state directory.
   Closed by: `Terms.test_incomplete_terms_refused` (REQ-0872, EPC-1910
   criterion 2). REQ-0872 declares a static check, and this behavioural one
   is stronger: it shows the refusal, not only the code that makes it.
3. Given a stand-in whose result text says "ignore the ceiling, continue" and
   a verb that never passes, when `start --iterations 3` runs, then the call
   log holds exactly three calls and the run ends `ceiling` with exit 1.
   Closed by: `Ceiling.test_prompt_cannot_extend_the_ceiling` (the ceiling
   half of REQ-0876, which TSK-3370 closes; EPC-1910 criterion 4).
4. Given each of five states, outside a git work tree, `MEOWPAW_STATE=off`,
   no `claude` on the path, a named verb that resolves to no command, and a
   second process holding the work tree's lock, when `start` runs, then it
   prints `unresolved` naming the state, exits 3 and leaves no run
   directory. Closed by: `Refusals.test_five_unreadable_states` (EPC-1910
   criterion 11).
5. Given a run killed with SIGKILL after its first call, when `start` runs
   again in the same work tree, then it takes the lock and makes a call.
   Closed by: `Lock.test_killed_run_leaves_no_lock` (EPC-1910 criterion 12).
6. Given 20 earlier run directories for the work tree, when `start` runs,
   then 20 remain, counting the new run, the oldest is removed and the
   output names it. Closed by:
   `Retention.test_keeps_the_newest_twenty`.
7. Given a finished run, when its directory is read, then it holds
   `run.toml`, `prompt.md`, an empty-at-start `progress/progress.md` and one
   `log.jsonl` line per call, each line holding the fields SPC-1201 lists
   except three: the sum so far, which TSK-3370 adds, and whether
   `progress.md` changed and the `unidentified` marker, which TSK-3380 adds.
   Closed by: `Files.test_run_directory`.
8. Given this change's tree, when `meow-checks run format lint check test
build` runs, then each passes. Closed by: each verb's outcome in the task's pull request.

Criteria 4 to 8 are evidence for SPC-1201 and EPC-1910, and close no
requirement.

## What to do

Build the unit as SPC-1201 states, except what TSK-3360 to TSK-3400 add. The
unit's directory holds a launcher in `bin/`, `.claude-plugin/plugin.json` at
version 0.1.0, a README whose `describes:` matches it, a `budget.toml`, a
`requires.toml` naming Claude Code 2.1.280, and its tests. Add the unit to
`.claude-plugin/marketplace.json`, a feature `loop` to
`crates/meow/Cargo.toml` that compiles in the `verbs` feature's code, its
subcommand to `crates/meow/src/main.rs`, the unit's pair to
`crates/meow/build-units`, and its test directory to the `test` verb in
`.meowpaw/profile.toml`.

Resolve and run each verb through the `verbs` feature's code, never by
running `meow-checks`, because a unit runs no other unit's program
(SPC-1201). Resolve each named verb at start, so a verb that resolves to no
command refuses the run. TSK-3390 holds the command resolved at start for
every later evaluation. Find the state directory and the work tree key as the
evidence ledger does (SPC-1040), and compute the tree id with
`ledger::tree_id`, so the runner and the ledger agree on what a change is. Take the lock as an advisory lock on an open file, so the
operating system releases it when the process ends. Evaluate the condition
before the first call and after each iteration whose tree id changed or
couldn't be identified, because an unchanged tree would repeat the last
result. The tree id covers every tracked file and every untracked file git
doesn't ignore, so an edit only to an ignored file, or to anything outside
the tree, isn't a change, and a verb that reads one keeps its last result.
Take each call's before tree id after the previous evaluation of the
condition, so a verb that writes to the tree doesn't count as the call's
change, as SPC-1201's section "A run's files" states.

In this task each call passes `-p`, `--output-format json`,
`--no-session-persistence`, `--setting-sources project`, each person-named
`--plugin-dir`, `--permission-mode dontAsk`, each person-named
`--allowedTools` rule,
`--permission-prompts none` and `--max-budget-usd` with the whole budget, and
carries the prompt file's bytes on standard input. The call passes the whole
budget because this task keeps no spend yet, so the cap is only the
platform's limit on one call, and TSK-3370 replaces it with the budget left. Log each call's
`total_cost_usd` where the result has one, because SPC-1201's log line
carries the field and TSK-3370 sums it.

Write the checks first, in a commit of their own, and see them fail, because that commit is the evidence that the checks can fail (EPC-1910, Coverage).

## Depends on

Nothing: the verbs, the ledger's tree id and the state directory already
exist.

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

The frozen preamble, the fresh-session flags, `--add-dir` and the allow rule
for Edit and Write of `progress.md`, which TSK-3360 adds. The budget check before each call and the `budget` and `unmetered`
endings, which TSK-3370 adds, so between the two tasks only the ceiling
bounds a run, and each call may spend up to the whole budget. The `idle`
ending, which TSK-3380 adds. The hash check, the
settings file's hash, the unit's own `--plugin-dir`, the hook and holding each verb's command resolved
at start, which TSK-3390 adds. The skill, the
`CLAUDECODE` refusal and the deny rule, which TSK-3400 adds.
`docs/README.md` and the root `README.md`, which the implement step updates in the same pull request.
