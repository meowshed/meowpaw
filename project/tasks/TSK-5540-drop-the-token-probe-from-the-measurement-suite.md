---
id: TSK-5540
artifact: task
status: done
revised: 2026-10-11
epic: EPC-2820
closes: []
issue: 1105
projected: b8cc6354911d
tracked: 200e6e655cbb
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Drop the token probe from the measurement suite

`tools/loop.py` measures a candidate by its score difference alone: the input
token probe, the `Tokens` column and the money `cost` column go, and with them
SPC-1020's stated cost in tokens and the landing clause "and the token cost
falls".

## Acceptance criteria

1. Given `tools/loop.py`, when its tests run, then no `input_tokens`,
   `token_cost` or tokens column remains, the delta and standard-error rules
   unchanged, and the `test` stage's loop tests pass. Closed by: the updated
   `tools/test_loop.py` and `mise run test`'s loop portion.
2. Given `project/specs/SPC-1020-measuring-the-harness.md`, when read, then it
   states no cost in tokens and its landing rule cites the difference alone.
   Closed by: the diff in the pull request.

## What to do

Delete `input_tokens` and `token_cost` from `tools/loop.py`, the `Tokens` and
cost cells from both tables, and the token clause from the landing rule and
the candidate loop's header. Remove the token assertions from
`tools/test_loop.py`. Edit SPC-1020's "What the run states" and "The loop"
sections. The published results keep their tables.

## Depends on

Nothing.

## Evidence

`tools/loop.py` lost `input_tokens`, `token_cost`, the empty probe, the
`Tokens` and money cells from both tables, the `--loads` argument and the
token clause of the landing rule, and the landing rule is the difference
alone (criterion 1). `tools/test_loop.py`'s 22 tests pass. SPC-1020 states no
cost in tokens and its landing rule cites the difference alone
(criterion 2).

## Left alone

`tools/measure_gate.py`, which reads a hook's verdict and counts nothing, and
`evals/thresholds.toml`, which states score thresholds.
