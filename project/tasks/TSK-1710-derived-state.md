---
id: TSK-1710
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1210
closes: [REQ-0527, REQ-0584, REQ-0591, REQ-0706, REQ-0712, REQ-0714]
issue:
---

# Show and status derive each requirement's state

Show and status derive each requirement's state, as ADR-1210 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a requirement closed by a done task in a verified epic, when `show` runs, then it prints the task and the verification. Closed by: a fixture.
2. Given a requirement no task closes, when `show` runs, then it prints "checked by nothing". Closed by: a fixture.
3. Given a verified epic with a finding on one of its tasks, when `status` runs, then it withholds "verified" and names the count. Closed by: a fixture.
4. Given a record outside any repository, when `status` runs, then it says the record is local to this machine. Closed by: a fixture.

## What to do

Make `show` print a requirement's derived state: each task closing it with its mark, and its epic's verification, or "checked by nothing". Make `status` count requirements by derived state, report an epic as verified only when `check` reports nothing on the epic, its decision or its tasks, and say the record is local to this machine where its root is under no version control.

## Depends on

Nothing. ADR-1210 is approved.

## Evidence

Not yet.

## Left alone

Reading tests that name a requirement, which ADR-1210 leaves.
