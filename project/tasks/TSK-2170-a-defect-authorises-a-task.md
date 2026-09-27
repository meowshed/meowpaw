---
id: TSK-2170
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1420
closes: [REQ-0352, REQ-0354, REQ-0374]
issue:
---

# A defect authorises a task directly, and `status` counts work by its authority

A task may name `bug: BUG-NNNN` in place of `epic`, the defect carries its
task's mark, and `paw` derives the task's state, readies it and counts it as
work a defect authorised. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given a fixture record with an approved defect carrying `- [x] T-001
TSK-0002` under `## Tasks` and a task naming `bug:` and closing a
   requirement, when `paw show` reads the requirement, then the task is done
   in the defect. Closed by: a fixture naming REQ-0354, seen failing first.
2. Given the same defect approved and its task not done, when `paw ready
implement TSK-0002` runs, then it exits 0; given the defect a draft, it
   exits 1 naming the defect. Closed by: fixtures naming REQ-0352.
3. Given a record with tasks under a decision's epic and under a defect, when
   `paw status` runs, then it prints how many tasks each kind authorised.
   Closed by: a fixture naming REQ-0374.
4. Given a task naming neither `epic` nor `bug`, or both, when `paw check`
   runs, then it reports the task. Closed by: a fixture.

## What to do

In `lib/layout.toml`, let a task carry `bug` in place of `epic`, and add `bug`
and `prompted-by` to the relations. In the record's program, read a defect's
`## Tasks` marks as an epic's, derive a task's state from its authorising
record whichever kind it is, let `ready implement` accept a task a defect
authorises, let `check frozen` allow a defect's Tasks and Closed by sections
to change after approval as an epic's marks do, and count tasks by authority
in `status`. Add `bug` to the task template and a `## Tasks` section to the
defect template. `meow-flow` moves to a new minor version.

## Depends on

Nothing. ADR-1440 is approved.

## Evidence

Not yet.

## Left alone

The triage rules, which TSK-2180 adds.
