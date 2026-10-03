---
id: TSK-5045
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2570
closes: [REQ-1666]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Migrate the smallest of the six source repositories onto the harness

The smallest of the six private harnesses RES-0002 describes drops its
private copy and installs this harness, and its own gate runs before and
after, by hand, as SPC-1090 states under "This repository's own work". One task, one branch, one pull request, one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given the repository's gate run before the migration, when the migration lands and the gate runs again, then it exits 0, and each behaviour the repository relied on is listed with the command that shows it still holds (REQ-1666). Closed by: the two gate runs and the list, cited in this task's Evidence.
2. Given a behaviour that stops working, when the migration finds it, then it is recorded as a defect against this harness before the task closes. Closed by: the defect's identifier in this task's Evidence.

## What to do

The repository is the owner's, outside this one, so the owner names which of
the six is the smallest and gives access to it. That is an open question,
and it blocks this task's implement step and nothing else. Run both gates by
hand, never in CI, because the owner keeps model calls out of CI. Record
the evaluation as this task's evidence, citing each command, its exit status
and its output.

## Depends on

- TSK-5040 (not blocking): a gap the migration finds is recorded by the rule that task states, and can be recorded by hand without it.

## Evidence

Not yet.

## Left alone

The other five repositories, each a later task of this epic.
