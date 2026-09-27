---
id: TSK-2300
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1470
closes: [REQ-0149, REQ-0151, REQ-0157, REQ-0822, REQ-0823, REQ-2202]
issue:
---

# The method skill dispatches the reviewer before each gate, and the review step dispatches a review of the session's own work

The method skill dispatches `record-reviewer` with the record's path alone,
repairs for at most two rounds, writes what stays open into the record, and
labels its gate report; the review step dispatches a review of work the
session produced. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the method skill and the review step, when they are read, then they
   carry the dispatch with the path alone, the two rounds, the Open review
   findings section, the label, the refusal to review the session's own
   record, and the self-assessed report. Closed by: the trace, naming each
   requirement.
2. Given evaluation cases for a session writing a draft decision, when they
   run by hand through the loop, then the session dispatches the agent naming
   only the path, and writes a finding left open after the second round into
   the record. Closed by: the loop's report, naming REQ-0149, REQ-0151,
   REQ-0822 and REQ-0823.
3. Given the changed skill, when `meow-author check` and `meow-author cost`
   run, then both exit 0. Closed by: their output.

## What to do

Change `plugins/meow-flow/skills/method/SKILL.md` and
`plugins/meow-flow/skills/method/steps/review.md`, add the evaluation cases,
and move the unit to its next patch version.

## Depends on

TSK-2290, whose agent the skill dispatches.

## Evidence

Not yet.

## Left alone

The agent, which TSK-2290 ships.
