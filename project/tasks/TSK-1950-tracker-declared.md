---
id: TSK-1950
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1310
closes: [REQ-1351, REQ-1372, REQ-1376, REQ-1380, REQ-1384, REQ-1402]
issue: 373
---

# The tracker is declared, optional, and projectable by hand

The tracker is declared, optional, and projectable by hand, as ADR-1310 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a profile with no tracker, when `project` runs, then it reports the tracker undeclared, names the section to declare, and creates nothing. Closed by: a fixture.
2. Given each other requirement this task closes, when its evidence is gathered, then the task records the file, the fixture or the command that shows it holds. Closed by: the evidence table.

## What to do

Add `[tracker] kind` to the profile template and have `project` report a profile declaring no tracker and do nothing. Write the docs section giving the `gh` commands that produce the same issue and fields by hand. Record the evidence that the method completes with no tracker and that the mapping is recoverable from the repository.

## Depends on

TSK-1930, whose command this extends.

## Evidence

Not yet.

## Left alone

Projecting the epic onto a milestone or a board, which ADR-1310 leaves.
