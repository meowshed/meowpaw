---
id: TSK-5570
artifact: task
status: done
revised: 2026-10-11
epic: EPC-2830
closes: []
issue: 1108
projected: 2b72a81fc153
tracked: 33d4eb275c2d
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Delete the runners and the `eval` task

The measurement's two runners and their tests leave the repository, and the
gate's task that ran them by hand goes from `mise.toml`.

## Acceptance criteria

1. Given `tools/`, when `find` looks for `loop.py` and `measure_gate.py`, then
   it matches nothing. Closed by: `find` in the pull request.
2. Given `mise.toml`, when `mise run all` runs, then no `eval` task exists and
   the gate passes as far as its pre-existing findings allow. Closed by: the
   gate's output in the pull request.

## What to do

Delete `tools/loop.py`, `tools/measure_gate.py` and `tools/test_loop.py`.
Remove the `[tasks.eval]` block from `mise.toml`. Nothing else reads the
runners: `grep` for `loop.py` and `measure_gate` over `tools/`, `crates/`,
`plugins/` and `packages/` confirms it, `tools/check_terms.py` excepted
(TSK-5580 removes the entry).

## Depends on

- TSK-5560 (not blocking): the requirements go in the same pull request, and
  nothing here reads them.

## Evidence

No `loop.py` or `measure_gate.py` remains under `tools/`, and
`tools/test_loop.py` went with them (criterion 1). The `eval` task is gone
from `mise.toml` (criterion 2).

## Left alone

The prose gate's `hand_run.py`, which measures the gate and stays, and every
workflow under `.github/workflows/`, which named the suite nowhere.
