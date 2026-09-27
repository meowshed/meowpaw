---
id: TSK-2160
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1410
closes: [REQ-1890, REQ-1892, REQ-1894, REQ-1896, REQ-1898, REQ-1900, REQ-1902]
issue:
---

# `meow-code:debug` holds how a defect is debugged

`meow-code` gains a second skill, loaded before the model looks for the cause
of a defect, carrying each rule ADR-1430 lists. One task, one branch, one pull
request, one review.

## Acceptance criteria

1. Given the skill, when it is read, then a labelled rule carries each
   requirement this task closes, and no rule names a requirement, a language
   or a tool. Closed by: a table in the evidence, and a search of the file.
2. Given the unit, when `mise run prompts` and `mise run budget` run, then both
   pass. Closed by: their output.
3. Given a scratch repository with a script printing a wrong value, and five
   sessions on each model with only the unit installed asked to find why and
   fix it, then the debugging skill loads before the first edit in at least
   four of five on each. Closed by: the runs' tool calls. Predicted: 5 of 5 on
   Opus 5.5 and at least 4 of 5 on Sonnet 5, as `meow-code:change` measured
   after BUG-1200.

## What to do

Write the skill with a description stating the obligation, shaped like the
measured description of `meow-code:change`, and the rules ADR-1430 lists,
each with its reason. Raise the unit's ceiling for the new description, move
the unit to 0.2.0, and add the skill to its page.

## Depends on

Nothing. ADR-1430 is approved.

## Evidence

Not yet.

## Left alone

The method's path for a defect, which a later decision settles.
