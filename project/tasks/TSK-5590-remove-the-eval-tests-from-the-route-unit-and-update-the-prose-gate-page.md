---
id: TSK-5590
artifact: task
status: done
revised: 2026-10-11
epic: EPC-2830
closes: []
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Remove the eval tests from the route unit and update the prose-gate page

The route unit's static test keeps what a program can read about the skill and
drops what read the deleted cases; the prose-gate unit's page keeps naming its
hand run where the hand run survives.

## Acceptance criteria

1. Given `plugins/meow-flow/tests/test_route.py`, when its suite runs, then
   the static checks on the skill pass and no test names `evals/`. Closed by:
   the suite's output in the pull request.
2. Given `plugins/meow-prose-gate/README.md`, when read, then its hand-run
   statement stands and names no runner that is gone. Closed by: reading it
   in the pull request.

## What to do

Delete the `RouteCases` class and the `EVALS`/case constants from
`plugins/meow-flow/tests/test_route.py`, keeping `SkillRoute` and
`RouteSkill`. Read `plugins/meow-prose-gate/README.md` where it names the hand
run or the runners, and update any line that names `tools/loop.py` or
`measure_gate.py`.

## Depends on

- TSK-5580 (blocking): the evals it reads are deleted by the other task.

## Evidence

`plugins/meow-flow/tests/test_route.py` keeps `SkillRoute` and `RouteSkill`
and names no `evals/` (criterion 1). `plugins/meow-prose-gate/README.md`
names its own `hand_run.py` and no runner that is gone (criterion 2).

## Left alone

The route skill itself, whose behaviour the deleted cases measured.
