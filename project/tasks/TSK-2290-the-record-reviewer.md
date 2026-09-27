---
id: TSK-2290
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1470
closes: [REQ-0132, REQ-0147, REQ-0819, REQ-2828, REQ-2830]
issue:
---

# `meow-flow` ships `record-reviewer`, with a question set per kind and read-only tools

The agent reviews one record against the questions ADR-1490 lists for its
kind and the two every kind gets, reports findings without editing, and opens
with its label. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the agent's file, when `meow-author check` and `meow-author cost`
   run, then both exit 0, and its front matter declares `Read`, `Grep` and
   `Glob` as its only tools. Closed by: their output, naming REQ-0819.
2. Given the agent's body, when it is read, then it carries each question set
   ADR-1490 lists, the two every kind gets, the rule to ask nothing `paw check`
   settles and to report each finding as a judgement, and the label. Closed
   by: the trace, naming REQ-2828, REQ-2830, REQ-0132 and REQ-0147.
3. Given evaluation cases for a draft decision with a rule given no reason and
   no cost section, and for a clean requirement, when they run by hand through
   the loop, then the agent reports both findings in the first, reports the
   second clean, and opens each report with its label. Closed by: the loop's
   report, naming REQ-2828 and REQ-2830.

## What to do

Write `plugins/meow-flow/agents/record-reviewer.md` and its evaluation cases
under `plugins/meow-flow/evals/`, state the agent on the unit's page, and move
the unit to its next minor version.

## Depends on

Nothing. ADR-1490 is approved.

## Evidence

Not yet.

## Left alone

The method skill and the review step, which TSK-2300 changes.
