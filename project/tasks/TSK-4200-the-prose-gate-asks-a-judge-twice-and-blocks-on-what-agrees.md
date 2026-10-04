---
id: TSK-4200
artifact: task
status: done
revised: 2026-10-03
realises: ADR-2390
closes: [REQ-3740, REQ-3742, REQ-3744, REQ-3746, REQ-3748, REQ-3750, REQ-3752]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Make the prose gate ask a judge twice and block only on what both judgements report

`meow-prose-gate check` gains the judged rules J1, J2 and J3. It asks a judge
twice, keeps a finding only where its span is in the text and both judgements
report it, and says so when it couldn't judge, as ADR-2390 and SPC-1010
state. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given a stub judge, set through `MEOW_PROSE_GATE_JUDGE`, that returns
   `J1` on `circling back` in both calls, when the gate checks
   `git commit -m "Stop circling back to the cache"`, then it exits 2 and
   prints `J1 | "circling back" | ...` (REQ-3744). Closed by: a fixture naming
   REQ-3744, seen failing first.
2. Given a stub judge that returns that finding in the first call and none in
   the second, when the gate checks the same command, then it exits 0 and
   prints nothing (REQ-3744). Closed by: a fixture naming REQ-3744.
3. Given a stub judge that returns `J3` on a span the command doesn't hold, in
   both calls, when the gate checks a plain body, then it exits 0 (REQ-3746).
   Closed by: a fixture naming REQ-3746.
4. Given a body holding `deep dive` and a stub judge that records each call to
   a file, when the gate checks it, then it exits 2 on P1 and the file records
   no call (REQ-3740). Closed by: a fixture naming REQ-3740.
5. Given each failure cause in turn, a judge command that doesn't exist, one
   that exits 1, one that sleeps 50 seconds and one that prints JSON outside
   the schema, when the gate checks a plain body, then it exits 0 and prints a
   `systemMessage` that names that cause (REQ-3748). Closed by: four fixtures
   naming REQ-3748.
6. Given the program's source, when a fixture reads the judge's command line,
   then it holds `--safe-mode`, `--tools ""`, `--no-session-persistence`,
   `--max-turns 1` and `--json-schema` (REQ-3750). Closed by: a fixture naming
   REQ-3750.
7. Given the schema the unit ships, when a fixture reads its `rule` field,
   then the field allows exactly `J1`, `J2` and `J3` (REQ-3742). Closed by: a
   fixture naming REQ-3742.
8. Given each hook in `hooks/hooks.json`, when a fixture reads it, then its
   `timeout` is 120 (ADR-2390). Closed by: a fixture naming ADR-2390.
9. Given `plugins/meow-prose-gate/evals/` with BUG-1230's four texts and one
   text per judged rule that breaks it, when the owner's hand run sends each
   through the installed gate three times, then the four texts pass in every
   run and each breaking text blocks in every run (REQ-3752). Closed by: the
   run's output in this task's pull request, as a smoke check.

## What to do

Add the judge to the `prose` feature in `crates/meow/`, behind the exact
rules: two `claude -p` calls started side by side with the flags ADR-2390
names, a 45-second limit on each, and the text passed as data inside a tag.
Ship the prompt and the schema inside `plugins/meow-prose-gate/`, and hold the
prompt to SPC-1030. Keep `MEOW_PROSE_GATE_JUDGE` for the fixtures alone, and
say so in the unit's README.

Raise each hook's `timeout` in `hooks/hooks.json` to 120. Update the unit's
README to state J1, J2 and J3, the two calls, their cost in time and usage,
and the not-checked message, and update `budget.toml`'s reasoning. The
permanent budget stays 0, because nothing loads on a turn.

Time the two calls on one ordinary publish, and put the wait in the pull
request, because ADR-2390 leaves it unmeasured.

## Depends on

Nothing.

## Evidence

Closed in the pull request from `feat/prose-gate-judge`, which closes
REQ-3740, REQ-3742, REQ-3744, REQ-3746, REQ-3748, REQ-3750 and REQ-3752. The
fixtures in `plugins/meow-prose-gate/tests/test_gate.py`, class
`TheJudgedRules`, close the criteria a program can check, each committed
first in a commit of its own:

1. `test_a_finding_both_judgements_report_blocks` (REQ-3744), seen failing
   first.
2. `test_a_finding_one_judgement_reports_passes` (REQ-3744). It passed before
   the judge existed, so it guards against a judge that blocks too eagerly.
3. `test_a_finding_on_a_span_the_text_lacks_passes` (REQ-3746), which passed
   first for the same reason.
4. `test_an_exact_finding_calls_no_judge` (REQ-3740), which passed first for
   the same reason.
5. `test_a_missing_judge_is_reported_not_checked`,
   `test_a_failing_judge_is_reported_not_checked`,
   `test_a_slow_judge_is_reported_not_checked` and
   `test_an_answer_outside_the_schema_is_reported_not_checked` (REQ-3748),
   each seen failing first.
6. `test_the_judge_loads_nothing` (REQ-3750), seen failing first.
7. `test_the_schema_allows_exactly_the_judged_rules` (REQ-3742), seen failing
   first.
8. `test_every_hook_waits_long_enough_for_the_judge` (ADR-2390), seen failing
   first.

The review inside the pull request added
`test_a_judged_span_inside_code_passes` (REQ-3746),
`test_a_judged_span_outside_code_still_blocks_where_it_also_appears_inside`
(REQ-3744), `test_a_failing_judge_names_its_last_error_line` and
`test_a_judge_whose_child_holds_its_output_is_stopped_at_the_limit`
(REQ-3748), each seen failing first, and rewrote criteria 1 and 2's fixtures
to give the second call another fix and to run both orders.

`meow-checks run format lint check test build` passed all five verbs on the
branch. Criterion 9 was run by hand, never in CI, on 2026-10-03 with Claude
Code 2.1.284, as `python3 plugins/meow-prose-gate/evals/hand_run.py 3`, after
the review's fixes: it exited 0 with 21 of 21 runs as wanted. The four
BUG-1230 texts passed in three runs of three, the J1, J2 and J3 texts each
blocked in three runs of three, and each pair of calls took 3 to 7 seconds. It
is a smoke check, and three runs show only a frequent false block. The agent
implementing the task made the run, and the owner didn't. The main session
accepted that run in place of the owner's, under the owner's standing
approval of 2026-10-03.

## Left alone

P1, P2 and P3, the commands the hook fires on, and how the program reads the
text from a command, because ADR-2390 keeps ADR-1600's decision on all of
them. `gh pr merge` stays outside the gate, as both decisions leave it.
