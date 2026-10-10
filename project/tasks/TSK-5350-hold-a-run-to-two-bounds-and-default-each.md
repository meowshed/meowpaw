---
id: TSK-5350
artifact: task
status: approved
revised: 2026-10-10
realises: ADR-2910
closes: [REQ-3724, REQ-3726, REQ-3728, REQ-3730, REQ-3732]
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Hold a run to two bounds and default each

`meow-loop` ends a run on the iteration ceiling or the time limit and on no
token count, runs a start command that omits a bound with its default, names
the bounds in force at the start, and accepts `--tokens` with a notice. One
task, one branch, one pull request, one review: the tests first, then the
change, its documentation and its marks.

## Acceptance criteria

1. Given a session transcript whose usage fields sum to 30 million tokens and
   a run started with `--iterations 10 --hours 4`, when the `Stop` hook runs
   after the first turn, then it doesn't end the run and blocks the stop with
   the frozen prompt (REQ-3732). Closed by: a crate test naming REQ-3732, seen
   failing first.
2. Given a run that has done its stated iterations, when the `Stop` hook runs,
   then the run ends as `ceiling`, and given one past its stated hours it ends
   as `time` (REQ-3724). Closed by: crate tests naming REQ-3724.
3. Given the source of `crates/meow/src/runloop.rs`, `run.toml` and `log.jsonl`
   as the hook writes them, when each is searched, then none holds an ending
   `tokens`, a `tokens` bound or a running token total (REQ-3732). Closed by:
   a crate test naming REQ-3732.
4. Given the prompt `/meow-loop:run`, when the `UserPromptSubmit` hook runs,
   then it starts a run whose `run.toml` holds `iterations = 10` and
   `hours = 4.0` and whose start context names both (REQ-3726, REQ-3728).
   Closed by: a crate test naming REQ-3726 and REQ-3728, seen failing first.
5. Given the prompt `/meow-loop:run --iterations 3`, when the hook runs, then
   the run holds `iterations = 3` and `hours = 4.0`, and the start context
   names `--hours 4` as a default (REQ-3726, REQ-3728). Closed by: a crate
   test naming REQ-3726.
6. Given the prompt `/meow-loop:run --iterations 10 --hours 4 --tokens
10000000`, when the hook runs, then it starts the run, `run.toml` holds no
   token bound and the start context says that the token bound no longer
   exists (REQ-3730). Closed by: a crate test naming REQ-3730, seen failing
   first.
7. Given the prompt `/meow-loop:run --hours 0`, when the hook runs, then no
   run starts and the report is `unresolved: --hours 0 is not a number above
0` (SPC-1201). Closed by: a crate test.

## What to do

Remove the token total, the `tokens` bound and the `tokens` ending from
`crates/meow/src/runloop.rs`: the flag's required check, the transcript sum
and the line it writes into `log.jsonl`, and drop `tokens` from `run.toml`.
Give `--iterations` and `--hours` the defaults ADR-2910 states, name the bounds
the run runs under in the start context, and accept `--tokens <t>` with the
notice REQ-3730 requires. Update `plugins/meow-loop/skills/run/SKILL.md`, the
unit's `README.md`, its manifest description and `tests/test_session_run.py`
to the two bounds and the defaults, and raise the unit's version by a minor,
because a command that was refused now starts a run. Raise the `meow-core`
requirement only if the unit's `requires.toml` pins the build that carries the
change.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

`meow-loop start`, the terminal runner, which REQ-3004 removes in its own
release. A measure of spend, which ADR-2910 doesn't settle.
