---
id: ADR-2900
artifact: adr
status: approved
revised: 2026-10-10
addresses: [REQ-3704, REQ-4900, REQ-4902]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2900. The driver is the one action the model may invoke

## Decision

`/meow-flow:run` drops `disable-model-invocation`, so the model can invoke it
through the `Skill` tool. Every other unit with side effects stays closed to
the model, and `/meow-loop:run` stays closed too, because only a person may
start a run (REQ-0894). REQ-4900 and REQ-4902 replace REQ-2680, and REQ-4900
states the exception.

The driver's description joins what `meow-flow` loads on every turn, so its
`budget.toml` rises by the length of that description.

Once this is accepted, a run's iteration reaches the driver and carries the
chain to its next stop (REQ-3704). Outside a run, a model can invoke the
driver too, and the skill's own role keeps that attended: with no run prompt
it stops at the first gate and waits for a person.

## Why

An iteration of a run is a prompt a `Stop` hook hands the model, and the model
can invoke only a skill the platform lists for it (RES-0320, conclusion 6).
The run skill's second step names a skill the model can't invoke, so no
iteration can do its work (BUG-1540).

## Alternatives

| Option                                          | Better at                    | Why it lost                                                                                                              |
| ----------------------------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Do nothing                                      | Keeps REQ-2680 whole         | A run can't do its work, and it still spends its bounds.                                                                 |
| Iteration loads `method` and repeats the driver | Keeps the driver closed      | The `method` skill is a step and holds none of the driver's rules, so the driver's text would be copied into the prompt. |
| Open the driver only while a run is active      | Keeps the driver closed idle | The platform's flag is a boolean in the file, so a hook can't flip it for one session.                                   |

## What it costs

The driver's description loads on every turn in every session, about a
hundred characters. A model that takes the driver's description as a prompt to
act may start the chain without being asked, and the skill's attended rule is
the only guard against it.

## What would reverse it

- A platform setting that lets a hook grant the model one skill for the length
  of a run. Then the flag returns and the grant replaces the exception.

## Consequences

REQ-2680 is withdrawn and REQ-4900 and REQ-4902 replace it. SPC-1030 cites the
new requirements. `plugins/meow-flow/skills/run/SKILL.md` and its mirror under
`packages/meow-flow` lose the flag, and `plugins/meow-flow/budget.toml` rises.
`meow-flow` is released.

## How I will know it was realised

1. `mise run budget` passes with the driver's description counted.
2. A run's iteration invokes `meow-flow:run` through the `Skill` tool and the
   tool doesn't refuse it.

## What this does not settle

- Whether a run's skill and the driver should be one unit.
- How a run restricts what a model that invokes the driver outside a run may
  merge or release.
