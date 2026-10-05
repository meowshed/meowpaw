---
id: TSK-2310
artifact: task
status: done
revised: 2026-09-27
epic: EPC-1480
closes: [REQ-0153, REQ-0159, REQ-0160, REQ-1759, REQ-3022, REQ-3026, REQ-3028]
issue: 529
projected: 0baf7ef6e8d2
---

# `tools/loop.py` reports what each result rests on and refuses what it can't hold

The loop runs both arms in classifier mode too, labels each case against a
margin, reports every rate's error and each run count, names the judge's
family and the threshold commit, and refuses an uncommitted threshold file and
a `baseline` grader. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given scores from both arms, when the loop labels a case, then an interval
   within 0.10 of zero reads `delete`, one clearing zero separates, and any
   other reads `undetermined: run more`. Closed by: unit tests naming
   REQ-3022, seen failing first.
2. Given classifier results, when the loop reports them, then each rate
   carries twice its standard error and each case its run count. Closed by:
   unit tests naming REQ-0160 and REQ-3026.
3. Given a judge identifier and a candidate model, when the loop writes its
   header, then it names the judge's family, calls a same-family result a
   smoke check, calls another family's result no claim, and calls a run of 3
   or fewer no claim. Closed by: unit tests naming REQ-3028 and REQ-3026.
4. Given a threshold file differing from the last commit, or a case with a
   `baseline` grader, when the loop starts, then it refuses and names why;
   given a case with no threshold, then it runs and gives no verdict; and the
   header names the threshold commit. Closed by: unit tests naming REQ-0159
   and REQ-0153.
5. Given a candidate and a baseline, when the loop decides the verdict, then
   it lands only within twice the combined error, and a case below its
   threshold gets no pass. Closed by: unit tests naming REQ-0159.
6. Given `meow-flow`'s cases, when the loop runs by hand, then it prints both
   arms, each rate's error, the run count and the judge's family. Closed by:
   its output, naming REQ-1759.

## What to do

Change `tools/loop.py` and add `tools/test_loop.py`, run by the `test` verb
with no model call, and point the `test` verb at it.

## Depends on

Nothing. ADR-1500 is approved.

## Evidence

Closes REQ-0153, REQ-0159, REQ-0160, REQ-1759, REQ-3022, REQ-3026 and
REQ-3028. `meow-verbs evidence format lint test` exits 0:

```text
format: passed, record 22800b5e1042, current at tree 722e4ed3c6c1
lint: passed, record 55ffcaa4ecd7, current at tree 722e4ed3c6c1
test: passed, record 562901be29ec, current at tree 722e4ed3c6c1
```

The `test` verb now runs `tools/test_loop.py`, whose 18 tests pass with no
model call; 17 of them failed on the loop before the change, and the 18th
covers the landing rule, which the loop already had. Each criterion's check:

1. `Labels`: delete, separates, undetermined and no arm without the unit
   (REQ-3022).
2. `Rates`: each rate's error and run count, and the case table printing them
   (REQ-0160, REQ-3026).
3. `Judge`: the family from the identifier, a same-family smoke check, another
   family still no claim, the judge as a candidate, and 3 runs supporting no
   claim (REQ-3028, REQ-3026).
4. `Refusals`: the threshold commit named, a differing threshold file refused,
   and a `baseline` grader found and refused (REQ-0159, REQ-0153).
5. `Verdicts`: landing within twice the combined error, a case below its
   threshold not meeting it, and a case with no threshold given no verdict
   (REQ-0159).
6. `python3 tools/loop.py plugins/meow-flow --mode classifier --model
claude-sonnet-5 --allow-tool Write --allow-tool Edit`, run by hand through
   the platform's `claude plugin eval` (REQ-1759), printed both arms, each
   rate's error, the run count, the judge's family and the threshold commit:

   ```text
   Judge claude-opus-5-5, of the claude family; 5 runs per arm.
   Thresholds as committed at c47579f 2026-09-27T19:01:02+02:00, before this run (REQ-0159).
   | baseline | ... | defect | 1.00 ±0.00 | 0.00 ±0.00 | +1.00 | 0.00 | 14 | separates | ...
   | baseline | ... | clean | 1.00 ±0.00 | 0.00 ±0.00 | +1.00 | 0.00 | 5 | separates | ...
   ```

   Every case separates: without the unit the agent doesn't exist, so each
   case scores 0.

The run shows a limit ADR-1500 didn't foresee: a rate of exactly 0 or 1 gets
an error of 0 from the formula the loop uses, which understates what 5 runs
can show. The label is still right here, because the delta of 1.00 clears
zero by any error 5 runs could have, but a case near the margin at 0 or 1
would be labelled with more confidence than it has.

## Left alone

The units' cases and thresholds, which their next run measures.
