---
id: TSK-2310
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1480
closes: [REQ-0153, REQ-0159, REQ-0160, REQ-1759, REQ-3022, REQ-3026, REQ-3028]
issue:
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

Not yet.

## Left alone

The units' cases and thresholds, which their next run measures.
