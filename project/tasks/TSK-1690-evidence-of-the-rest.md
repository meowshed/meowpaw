---
id: TSK-1690
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1200
closes:
  [
    REQ-1726,
    REQ-1734,
    REQ-1744,
    REQ-1746,
    REQ-1748,
    REQ-1750,
    REQ-1752,
    REQ-1754,
    REQ-1756,
    REQ-1758,
    REQ-1762,
    REQ-1766,
  ]
issue: 272
---

# Record the evidence for the attributes that already hold

Record the evidence for the attributes that already hold, as ADR-1200 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given each requirement this task closes, when its evidence is gathered at the current revision, then the task records a command and its output, or the file and line, that shows it holds. Closed by: the evidence table.

## What to do

Add a rule to the `method` skill separating what a report verified from what it assumed. For each other requirement this task closes, gather the evidence at the current revision and record it: the launchers' fallbacks, the drafts-only scope and the migrations, the kernel installed alone, the units' descriptions, the record's syntax, the gate run locally, the stub runs, the tools in `mise.toml`, and the absence of any spend without a person.

## Depends on

Nothing. ADR-1200 is approved.

## Evidence

Not yet.

## Left alone

REQ-1738, REQ-1759 and REQ-1764, which ADR-1200 leaves.
