---
id: TSK-3370
artifact: task
status: done
revised: 2026-09-30
epic: EPC-1910
closes: [REQ-0870, REQ-0876, REQ-0878]
issue: 727
projected: da48b31a3ef7
---

# Check the budget before each call, and end a run that can't be metered

Before each call the runner adds the largest single call's spend so far to
the spend so far, and ends the run `budget` if the sum would pass the budget.
A call that reports no cost ends the run `unmetered`, and a call that hit the
platform's own cap ends it `budget`. The budget then bounds the run before
the call that could pass it starts. This task also closes REQ-0870 and
REQ-0876, because each names a budget beside the condition or the ceiling
that TSK-3350 built, and this task is where the runner first holds it. One
task, one branch, one pull request, one review.

**Amended by ADR-2300.** Its verbs criterion is closed by the pull request's gate, since no run output is kept, and it names the checks unit `meow-checks`.

## Acceptance criteria

Every check below lives in `plugins/meow-loop/tests/test_loop.py` and counts
what it matched, failing on a count of zero where one was expected (EPC-1910
criterion 13).

1. Given `--budget-usd 1.00`, `--iterations 10`, a verb that never passes and
   a stand-in that ignores `--max-budget-usd` and costs 0.60 a call, when the
   run ends, then the call log holds exactly one call, `run.toml` records
   `budget` and the runner exits 1; given 0.30 a call, then it holds exactly
   three calls and the fourth is never started. The stand-in ignores the cap,
   so the ending can only come from the runner. Closed by: `Budget.test_forecast_before_the_call`
   (REQ-0878; the budget half of REQ-0870 and of REQ-0876, whose other halves
   TSK-3350's criteria 1 and 3 close; EPC-1910 criterion 5).
2. Given a stand-in that prints no result, and one whose result has no
   `total_cost_usd`, when each run ends, then the call log holds one call,
   `run.toml` records `unmetered` and the runner exits 1. Closed by: `Budget.test_unmetered`
   (EPC-1910 criterion 10).
3. Given `--budget-usd 1.00`, `--iterations 10`, a verb that never passes and
   a stand-in costing 0.01 a call whose result has the subtype
   `error_max_budget_usd`, when the run ends, then the call log holds exactly
   one call, `run.toml` records `budget` and the runner exits 1. The forecast
   can't trip at that cost, so only the subtype ends the run. Closed by:
   `Budget.test_platform_cap_ends_the_run`.
4. Given `--budget-usd 1.00`, `--iterations 2` and a stand-in costing 0.30 a
   call, when the recorded argv are read, then the `--max-budget-usd` values
   are 1.00 and 0.70, compared as numbers to within 0.000001. Closed by:
   `Budget.test_cap_is_the_budget_left`.
5. Given a run of three calls at 0.30 each, when `log.jsonl` is read, then its
   lines carry the sums 0.30, 0.60 and 0.90, compared as numbers to within
   0.000001, because a sum in binary floating point needn't equal the decimal
   figure exactly. Closed by:
   `Budget.test_sum_so_far_is_logged`.
6. Given this change's tree, when `meow-checks run format lint check test
build` runs, then each passes. Closed by: each verb's outcome in the task's pull request.

## What to do

Add the third check before each call and steps 3 and 4 after it, as
SPC-1201's section "The loop" states, in the order it gives. Add the sum so
far to each `log.jsonl` line, the field TSK-3350's criterion 7 leaves to this
task. Pass `--max-budget-usd` as the budget minus the spend so far, replacing
the whole budget TSK-3350 passes, as SPC-1201's section "Each call" states.

Raise `meow-loop`'s minor version in `plugin.json`, and its README's
`describes:` with it, because a run gains two endings.

Write the checks for criteria 1 to 5 first, in a commit of their own, and
see them fail, because that commit is the evidence that the checks can fail (EPC-1910, Coverage). A check that already passes on
TSK-3350's tree shows nothing this task added, so rewrite it until it
fails there.

## Depends on

TSK-3350, because this task adds a check to the loop that task writes.

## Evidence

`run` in `crates/meow/src/runloop.rs` keeps the spend so far and the largest
single call's cost. Before each call it ends the run `budget` where their sum
is above the budget. After each call it writes the log's line with `sum_usd`,
ends the run `unmetered` where the result holds no cost, adds the cost, and
ends the run `budget` where the result's subtype is `error_max_budget_usd`,
all before it evaluates the condition. `call` passes `--max-budget-usd` as
the budget less the spend so far.

Criteria 1 to 5 are closed by the checks they name, in
`plugins/meow-loop/tests/test_loop.py`:

1. `Budget.test_forecast_before_the_call`
2. `Budget.test_unmetered`
3. `Budget.test_platform_cap_ends_the_run`
4. `Budget.test_cap_is_the_budget_left`
5. `Budget.test_sum_so_far_is_logged`

No criterion rests on judgement. The five checks failed first, in the commit
that holds them alone, where the `test` verb exited 1. That commit also
changes `Files.test_run_directory`, which asserted the log held no sum and now
reads the two sums, and it failed there too. Criterion 6 is closed by the
pull request, where `format`, `lint`, `check`, `test` and `build` each pass on
the change's tree.

I made three choices the task leaves open. The log's field is `sum_usd`, the
name TSK-3350's check already used for its absence, and it is `null` on the
line of a call that reported no cost. A cost that is negative or not finite
counts as no cost, because adding it would lower the spend or make it
unreadable. The run prints one line saying why it ended before its last line,
such as the spend, the largest call and the budget.

I made two more choices in review. A sum may pass the budget by a billionth
of a dollar and still count as within it, because 0.2 + 0.1 is above 0.3 in
binary floating point and the specification says "at most the budget". The
cap a call gets is the budget left to six decimal places.

SPC-1201 says under "The terms" that the budget reaches `claude` as typed.
After this task the first call gets the number, so `1.00` arrives as `1`, and
that sentence needs a change of its own.

No real call ran, so the subtype `error_max_budget_usd` and the field
`total_cost_usd` are as RES-0300 recorded them and the stand-in prints them.
`meow-loop` goes to 0.3.0, and its README states the two endings, the check
before a call and the sum in the log.

## Left alone

A call that costs more than the largest before it, which can still pass the
budget by as much as the platform lets a call pass its own cap, as ADR-2010's
costs say. A meter other than the platform's own estimate, because
`total_cost_usd` is the only cost a call reports (RES-0300), and ADR-2010's
reversals name another meter only if the platform stops reporting it.
