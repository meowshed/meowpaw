---
id: BUG-1250
artifact: bug
status: approved
severity: major
violates: REQ-0208
enters: cover
found: 2026-09-28
revised: 2026-09-28
issue:
---

# `paw status` names document for an epic with no tasks, and `paw ready document` refuses it

`paw status` reads an epic with no tasks as having every task done and names
`next: document, then verify` for it, while `paw ready document` and `paw
ready verify` refuse the same epic with `lists no tasks`. So the driver tells
a person what the next invocation will do, and the next invocation can't do
it, whatever anyone approves.

## Reproduction

`main` after #621, with `meow-flow` 0.34.0 built by `crates/meow/build-units`.

1. EPC-1590 realises ADR-1600 and lists no tasks, because the decision's work
   landed as TSK-2470 under BUG-1230 before the epic existed. It names every
   requirement ADR-1600 addresses under `## Not covered`, and `paw check`
   reports no coverage finding for it.
2. `plugins/meow-flow/bin/paw status` prints, under ADR-1600, `next:
document, then verify EPC-1590 (0 tasks done)`.
3. `plugins/meow-flow/bin/paw ready document EPC-1590` prints `paw ready
document: not ready` and `EPC-1590 lists no tasks`, and exits 1.

## What the system does

The two commands disagree about one record. `status`'s `position` finds no
open task and names document. The `document` and `verify` gate in `ready`
refuses any epic whose task list is empty.

## What it should do, and why

The driver has to report what its next invocation will do (REQ-0208), so the
two commands must agree. An epic with no tasks of its own is legitimate when
it names every requirement its record addresses under `## Not covered`, which
the coverage check already accepts: its work was done elsewhere, and only
documenting and verifying it remain. Such an epic is ready for document and
verify. An epic with no tasks that leaves an addressed requirement unnamed is
refused, as now, and `status` names that refusal where it would have named a
step.

## Triage

It enters at cover, because the requirement is right and the program breaks
it. Major, because the record's own driver can't move a legitimate record
forward, and a person can only work around it by adding a task the decision
never asked for.

## Closed by

The reproduction as fixtures in `plugins/meow-flow/tests/test_record.py`: an
epic with no tasks naming every addressed requirement under Not covered is
ready for document and verify, and `status` names document; one leaving a
requirement unnamed is refused, and `status` names the refusal.

## Tasks

- [ ] T-001 TSK-2560 make `ready` and `status` agree on an epic with no tasks,
      in `crates/meow/src/record.rs`
