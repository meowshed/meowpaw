---
id: TSK-4110
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2300
closes:
  [
    REQ-0870,
    REQ-0876,
    REQ-0878,
    REQ-0882,
    REQ-0884,
    REQ-0886,
    REQ-0892,
    REQ-2654,
    REQ-2656,
    REQ-2658,
    REQ-3702,
    REQ-3704,
    REQ-3706,
    REQ-3708,
    REQ-3710,
  ]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Decide each iteration in the `Stop` hook

`meow-loop stop` decides after every turn whether the run's next iteration
starts. It logs the iteration, checks the five endings in the order SPC-1201
gives under "Each iteration", and otherwise blocks the stop with the frozen
prompt. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given an active run and a fixture record with one requirement open, when
   `meow-loop stop` runs, then it prints `decision: "block"` with the frozen
   prompt naming the run id and the progress file, byte for byte the same on
   two iterations (REQ-3702, REQ-0870). Closed by: a fixture naming REQ-3702,
   seen failing first.
2. Given the same run after the fixture record has no requirement and no
   defect open, and one postponed requirement, when the hook runs, then it
   allows the stop and `run.toml` records `finished` (REQ-3704, REQ-3706,
   REQ-0884). Closed by: a fixture naming REQ-3704.
3. Given a run whose iterations reached `--iterations`, whose start is more
   than `--hours` ago, or whose transcript's usage plus its largest iteration
   exceeds `--tokens`, when the hook runs, then the run ends `ceiling`, `time`
   or `tokens` (REQ-3708, REQ-0876, REQ-0878). Closed by: three fixtures
   naming REQ-3708.
4. Given two iterations in a row with the tree id, the open counts and
   `progress.md` unchanged, when the hook runs, then the run ends `stuck` and
   the `systemMessage` names the counts (REQ-3710, REQ-0886). Closed by: a
   fixture naming REQ-3710.
5. Given any iteration, when the hook runs, then `log.jsonl` gains one line
   with the iteration, the tree ids, the open counts, whether `progress.md`
   changed and the tokens so far (REQ-2654, REQ-0892, REQ-0882). Closed by: a
   fixture naming REQ-2654.
6. Given each ending, when the run ends, then `run.toml` holds exactly one of
   the six endings, and an ending reverts no file in the work tree (REQ-2658,
   REQ-2656). Closed by: a fixture naming REQ-2658.
7. Given no active run for the session's id, when the hook runs, then it
   allows the stop and writes nothing. Closed by: a fixture.

## What to do

Add the `stop` subcommand and its `Stop` hook entry. Count the open work with
the `record` code `paw status` uses, read the tree id with `ledger::tree_id`,
and sum tokens from the transcript path in the hook input. Where a state can't
be read, allow the stop, write no ending and report it, as SPC-1201's failure
paths state. Bump `meow-loop` as a `feat`.

## Depends on

- TSK-4100 (blocking): the hook reads the run state the start writes.

## Evidence

Not yet.

## Left alone

What an iteration does, which `/meow-flow:run` decides and TSK-4130 changes.
