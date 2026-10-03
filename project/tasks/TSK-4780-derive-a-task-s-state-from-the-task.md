---
id: TSK-4780
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2460
closes: [REQ-2897]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Derive a task's state from the task, and drop the per-task mark from a draft epic

A task under an epic is done once its Evidence is written past "Not yet." and
dropped once it is withdrawn, rejected or superseded, an approved epic with
marks keeps them, and `paw check` fails a draft epic that carries a status per
task, as SPC-1090 states under "The gate" and SPC-1070 under "The layout".
One task, one branch, one pull request, one review: the tests first, then the
change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture draft epic with an entry `- [ ] T-001 TSK-0001 ...`, when
   `paw check` runs, then it fails naming the line, and given the entry
   `- T-001 TSK-0001 ...`, it passes; the same entry in an approved epic
   passes (REQ-2897). Closed by: a crate test naming REQ-2897, seen failing
   first.
2. Given a fixture epic with unmarked entries and a task whose Evidence is
   written, when `paw status` and `paw ready implement` run, then the task
   reads as done, and a withdrawn task as dropped. Closed by: a crate test.
3. Given a fixture approved epic with marks, when `paw status` runs, then
   `[x]` and `[~]` still decide done and dropped, and the count of tasks done
   is the same before and after the change. Closed by: a crate test.
4. Given this repository's record, when `paw status` runs before and after
   the change, then every decision's line is the same. Closed by: both
   outputs in the pull request.

## What to do

Change how the `record` feature of `crates/meow/` derives a task's state, as
SPC-1090 states, reading both forms, which is the expand step method rule M14
names; name in the pull request the release of `meow-flow` that would remove
the reading of marks, and say no migration is planned because ADR-2590
excuses the approved epics. Add the draft rule to the epic kind in
`plugins/meow-flow/lib/layout.toml`.

Change `plugins/meow-flow/templates/epic.md` to the entry form SPC-1090 states
under "Templates", and drop its Marks section. Change the method's
`steps/epic.md` where it names marks, and `meow-prose`'s
`skills/writing/types/record/epic.md`, whose Marks section names them, each
held to SPC-1030 and its unit's `budget.toml`. In `CLAUDE.md`'s
`artifacts_stay_current`, say a task is marked complete by its Evidence, in
the commit that completes it.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

The approved epics, which keep their marks, and a defect's `## Tasks`, which
ADR-2590 doesn't address, so a defect still marks its tasks.
