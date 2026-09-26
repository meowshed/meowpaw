---
id: TSK-1670
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1200
closes: [REQ-1720, REQ-1722, REQ-1724, REQ-1728, REQ-1730, REQ-1732]
issue:
---

# Read-only commands write nothing, and an index is written atomically

Read-only commands write nothing, and an index is written atomically, as ADR-1200 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a record, when each read-only command runs, then the tree's hashes are unchanged and its output is identical run twice. Closed by: a fixture.
2. Given `index --write`, when it runs, then no temporary file is left and the index is whole. Closed by: a fixture.

## What to do

Write a fixture that hashes the tree before and after each read-only command, `check`, `check frozen`, `status`, `status --waiting`, `ready`, `template`, `show`, `index` without `--write`, `new` and `find`, and runs each twice for identical output. Make `index --write` write a temporary file beside the index and rename it into place.

## Depends on

Nothing. ADR-1200 is approved.

## Evidence

Not yet.

## Left alone

REQ-1738, REQ-1759 and REQ-1764, which ADR-1200 leaves.
