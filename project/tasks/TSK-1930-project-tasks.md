---
id: TSK-1930
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1310
closes:
  [
    REQ-1350,
    REQ-1352,
    REQ-1354,
    REQ-1355,
    REQ-1356,
    REQ-1360,
    REQ-1368,
    REQ-1382,
    REQ-1386,
    REQ-1396,
  ]
issue:
---

# Project an approved epic's tasks onto issues

Project an approved epic's tasks onto issues, as ADR-1310 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given an approved epic with two tasks, when `project` runs, then it creates two issues citing each task's requirements and dependencies with the marker, writes `issue:` and `projected:` on each task, and reads both back. Closed by: a fixture.
2. Given the same epic, when `project` runs again, then it creates and changes nothing. Closed by: a fixture.
3. Given a draft epic, when `project` runs, then it creates nothing. Closed by: a fixture.
4. Given an approved task whose `projected:` changed, when `check frozen` runs, then it passes. Closed by: a fixture.

## What to do

Add `meow-github project <epic>`: refuse an epic that isn't approved; for each task create an issue titled with its identifier and title, its body citing the epic, the requirements it closes and its dependencies with their reasons, ending with a marker naming the task and its fingerprint; write `issue:` and `projected:` on the task; read each issue back and report a mismatch; and change nothing for a task already projected at its fingerprint. Let `meow-method check frozen` accept a change to an approved task's `projected:`.

## Depends on

Nothing. ADR-1310 is approved.

## Evidence

Not yet.

## Left alone

Projecting the epic onto a milestone or a board, which ADR-1310 leaves.
