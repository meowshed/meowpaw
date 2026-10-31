---
id: BUG-1540
artifact: bug
status: done
severity: critical
violates: REQ-3704
enters: requirements
found: 2026-10-10
revised: 2026-10-10
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A run cannot start an iteration, because the driver it repeats is closed to the model

Every iteration of a `meow-loop` run is told to run `/meow-flow:run`, and the
skill sets `disable-model-invocation: true`, so the model can't run it and the
iteration does no work.

## Reproduction

Seen with Claude Code on macOS (arm64), `meow-loop` 0.13.0 and `meow-flow`
0.50.0, at revision `04247e7b`.

1. Type `/meow-loop:run --iterations 10 --hours 4 --tokens 10000000` in a
   session on a repository with an open requirement.
2. Let the iteration follow the `run` skill's second step, which says to run
   `/meow-flow:run`.

## What the system does

The `Skill` tool refuses the call with `Skill meow-flow:run cannot be used
with Skill tool due to disable-model-invocation`. The iteration writes "no
work done" into the progress file and ends. The `Stop` hook then blocks the
stop and repeats the same prompt, so each iteration up to the ceiling does
nothing, and the run ends as `stuck` after two of them (REQ-3710).

## What it should do, and why

REQ-3704 says a run repeats iterations of `/meow-flow:run` until nothing is
open. A run the person chose and paid for (REQ-0894) can't repeat a skill the
model is forbidden to invoke. REQ-2680 forbids the invocation for every unit
with side effects, and the driver has side effects, so two requirements in
force contradict each other for this one unit. RES-0320 conclusion 6 records
the platform's behaviour: the model can't start such a skill.

## Triage

It enters at requirements, because the code does what REQ-2680 asks and the
requirement is the part that is wrong for the driver. Severity is critical:
`meow-loop` can't do the one thing it exists for, and the run still spends
its iterations, hours and tokens.

## Closed by

`mise run budget` passes with the driver's description counted, and the
`run` skill carries no `disable-model-invocation`. A run's iteration then
reaches the driver through the `Skill` tool.

## Tasks

- [x] T-001 TSK-5340 let the model invoke the driver, and count its description in the budget (done: pull request 891)
