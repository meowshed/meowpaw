---
id: TSK-1700
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1210
closes: [REQ-0704, REQ-0710]
issue: 281
---

# The check reports work left unmarked and identifiers that resolve to nothing

The check reports work left unmarked and identifiers that resolve to nothing, as ADR-1210 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a task with evidence and an epic marking it `[ ]`, when `check coverage` runs, then it reports the task. Closed by: a fixture.
2. Given a task closing a withdrawn requirement in an unverified epic, when `check coverage` runs, then it reports the task. Closed by: a fixture.
3. Given a body naming an identifier with no file, when `check relations` runs, then it reports the line. Closed by: a fixture.

## What to do

In `check coverage`, report a task whose Evidence section holds more than "Not yet." while its epic marks it `[ ]`, and a task closing a withdrawn requirement in an epic with no `checked-at`. In `check relations`, scan each record's body for identifiers of a known kind and report one with no file. Fix what the new findings report in this repository's own record in the same change.

## Depends on

Nothing. ADR-1210 is approved.

## Evidence

Not yet.

## Left alone

Reading tests that name a requirement, which ADR-1210 leaves.
