---
id: TSK-2000
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1320
closes:
  [
    REQ-1296,
    REQ-1298,
    REQ-1306,
    REQ-1320,
    REQ-1322,
    REQ-1324,
    REQ-1328,
    REQ-2534,
    REQ-2536,
    REQ-2538,
    REQ-2820,
    REQ-2822,
  ]
issue:
---

# The commit skill carries the branching and merging rules

The commit skill carries the branching and merging rules, as ADR-1320 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given the skill, when the trace is read, then each requirement this task closes maps to a labelled rule that exists in it, or to recorded evidence. Closed by: the trace table and a script finding each label.

## What to do

Add rules to `meow-scm`'s `commit` skill for the requirements this task closes that no program settles, and record the evidence for the signing rules that already hold. Record the trace under Evidence.

## Depends on

Nothing. ADR-1320 is approved.

## Evidence

Not yet.

## Left alone

A version control tool other than git, which ADR-1320 leaves.
