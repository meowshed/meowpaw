---
id: TSK-1940
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1310
closes: [REQ-1353, REQ-1378, REQ-1388, REQ-1392, REQ-1394, REQ-1400]
issue:
---

# Report where the record and the tracker disagree

Report where the record and the tracker disagree, as ADR-1310 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a task changed since it was projected, when `project` runs, then it updates the issue and `projected:`. Closed by: a fixture.
2. Given an issue edited on GitHub, when `project` runs, then it reports the disagreement and leaves the issue as it is. Closed by: a fixture.
3. Given an issue closed while its task is unmarked, when `project --check` runs, then it reports it and writes nothing. Closed by: a fixture.

## What to do

Make `project` update the issue of a task changed since it was projected, report an issue edited on GitHub while its task is unchanged without overwriting it, and report an issue closed on GitHub while the epic leaves its task unmarked. Add `--check`, which reports each task's state and writes nothing. Never write an issue's state.

## Depends on

TSK-1930, whose command this extends.

## Evidence

Not yet.

## Left alone

Projecting the epic onto a milestone or a board, which ADR-1310 leaves.
