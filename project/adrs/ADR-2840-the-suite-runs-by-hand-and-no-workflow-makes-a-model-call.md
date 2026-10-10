---
id: ADR-2840
artifact: adr
status: done
revised: 2026-10-10
addresses: [REQ-3035]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2840. The measurement suite runs by hand, and no workflow makes a model call

## Decision

I withdraw REQ-3034, which asked that the measurement suite run on a schedule,
and replace it with REQ-3035: the suite runs by hand on the owner's machine,
and no workflow under `.github/workflows/` runs it or holds a model
credential. `tools/check_workflows.py` fails the gate on a workflow that
names the suite's `eval` task or a model credential, so the rule holds without
a person reading each workflow.

Once this is accepted, the record no longer asks for something the repository
refuses to do, and REQ-3038 keeps a new model as the reason to run the suite.
The suite still has no schedule, so a regression in a prompt that nobody ran
the suite against stays unseen until the next run by hand.

## Why

ADR-2690 named the conflict and left it for this decision: the owner keeps
model calls out of CI and runs evaluations by hand, so REQ-3034 and the owner's
rule can't both stand. TSK-1210 already built the by-hand run as an `eval` task
kept out of `all` (REQ-3038), so withdrawing the schedule removes a
requirement and builds nothing. RES-0266 records that a measurement is a real
model call, which is the reason both the schedule and the ban exist.

## Alternatives

| Option                                       | Better at                               | Why it lost                                                                                  |
| -------------------------------------------- | --------------------------------------- | -------------------------------------------------------------------------------------------- |
| Do nothing                                   | No work                                 | `paw status` keeps REQ-3034 as named by no task, and no task can close it without a workflow |
| Add a scheduled workflow that runs the suite | A regression seen without anyone asking | It puts a model call and a credential into CI, which the owner has ruled out                 |
| Keep the requirement and postpone it         | Keeps the record's wish visible         | A postponement names a condition that would lift it, and the owner has named none that would |

## What it costs

The suite has no scheduled run. A prompt can regress between two runs by hand, and
nothing flags it until someone runs the suite at a release or on a new model.

## What would reverse it

- The owner lifts the ban on model calls in CI, or asks for a scheduled run.
  While neither happens, the schedule has no home.

## Consequences

REQ-3034 is withdrawn and REQ-3035 states the obligation that replaces it.
SPC-1020 and SPC-1210 state the new rule, and `tools/check_workflows.py` gains
one rule with its tests. One task, TSK-5250, realises the decision.

## How I will know it was realised

1. A workflow that names `mise run eval` or a model credential fails
   `tools/check_workflows.py`, naming the file and the line (REQ-3035).
2. `paw status` lists no requirement named by no task.

## What this does not settle

- Whether the suite should run at every release. The owner runs it then
  today, and no requirement says how often, so this decision adds none.
