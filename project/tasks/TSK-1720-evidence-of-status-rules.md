---
id: TSK-1720
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1210
closes:
  [
    REQ-0510,
    REQ-0516,
    REQ-0518,
    REQ-0519,
    REQ-0582,
    REQ-0586,
    REQ-0690,
    REQ-0694,
    REQ-0696,
    REQ-0716,
  ]
issue:
---

# Record the evidence for the status rules that already hold

Record the evidence for the status rules that already hold, as ADR-1210 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given each requirement this task closes, when its evidence is gathered at the current revision, then the task records a command and its output, or the file and line, that shows it holds. Closed by: the evidence table.

## What to do

Gather, at the current revision, the evidence that each requirement this task closes already holds, and record it: the stored status vocabulary in `lib/layout.toml`, the amendment path `check frozen` holds, the layout by kind and the `epic` field, the record under version control, the rule on marking a task in the commit that closes it, and `new` allocating after approval.

## Depends on

Nothing. ADR-1210 is approved.

## Evidence

Not yet.

## Left alone

Reading tests that name a requirement, which ADR-1210 leaves.
