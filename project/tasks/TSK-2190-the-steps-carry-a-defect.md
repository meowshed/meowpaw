---
id: TSK-2190
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1420
closes: [REQ-0348, REQ-0350, REQ-3170, REQ-3174]
issue: 477
projected: 8e1d480d3f9f
---

# The implement and verify steps carry the rules on a defect

The implement step begins a defect's task from its reproduction and records a
gate-caught defect without a record of its own, and the verify step closes an
epic around an open defect only as ADR-1440 says. One task, one branch, one
pull request, one review.

## Acceptance criteria

1. Given `steps/implement.md` and `steps/verify.md`, when they are read, then
   a labelled rule carries each requirement this task closes, and no rule
   names a requirement, a language or a tool. Closed by: a table in the
   evidence, and a search of both files.
2. Given the step files, when `mise run prompts` runs, then it passes. Closed
   by: its output.

## What to do

Add rules to `steps/implement.md`: a defect's task begins by running its
reproduction and seeing it fail; a defect's task restores a requirement in
force and needs no new decision; a defect a gate caught and the same change
closed needs no record of its own. Add a rule to `steps/verify.md` on closing
an epic while a defect it uncovered is open.

## Depends on

Nothing. It changes only step files.

## Evidence

Not yet.

## Left alone

The record's program, which TSK-2170 and TSK-2180 change.
