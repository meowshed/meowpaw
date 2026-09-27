---
id: TSK-2210
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1430
closes:
  [
    REQ-1116,
    REQ-1118,
    REQ-1126,
    REQ-2680,
    REQ-2682,
    REQ-2684,
    REQ-2686,
    REQ-2690,
    REQ-2692,
    REQ-2706,
    REQ-2708,
  ]
issue:
---

# `meow-author:write` carries the rules a program can't settle

The unit gains a skill, loaded before a skill, agent, output style or hook
prompt is written or changed, whose rules carry each requirement this task
closes. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the skill, when it is read, then a labelled rule carries each
   requirement this task closes, and no rule names a requirement, a language
   or a tool. Closed by: a table in the evidence.
2. Given the unit, when `meow-author check`, the budget check and the prompt
   form run, then all pass. Closed by: their output.
3. Given five sessions on each of Sonnet 5 and Opus 5.5 with only the unit
   installed, asked to write a skill, then the skill loads before the first
   write in at least four of five on each. Closed by: the runs' tool calls.

## What to do

Write the skill with a description stating the obligation, shaped like the
measured descriptions of `meow-code`'s skills, and every rule ADR-1450 lists,
those the program also checks included, each with its reason. Measure its
loading on near misses that change code as well as on requests to write a
skill. Point to SPC-1030's vocabulary through the rules
themselves, since the skill ships and the specification doesn't. Raise the
unit's ceiling for the description, and add the skill to the unit's page.

## Depends on

TSK-2200, because the skill ships in the unit it creates.

## Evidence

Not yet.

## Left alone

The context cost of material, which a later decision settles.
