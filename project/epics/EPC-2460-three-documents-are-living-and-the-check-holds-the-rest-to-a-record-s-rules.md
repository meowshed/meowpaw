---
id: EPC-2460
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2590
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Three documents are living, and `paw check` holds every other kind to a record's rules

Realises exactly one authorising record, ADR-2590, which amends ADR-2300: a
task's state is read from the task itself, where ADR-2300 read it from a
mark in its epic.
The epic is complete when `paw check` holds the living kinds apart from the
records as SPC-1070 states, and a task is done or dropped as SPC-1090 states
under "The gate", with an epic carrying no status per task.

## Acceptance criteria

Taken from ADR-2590's list of how it will be known realised:

1. `paw check` fails a fixture requirement with `status: live` (REQ-0610).
2. It fails a fixture specification with a struck-through line (REQ-0632).
3. It fails a withdrawn fixture whose first line names no identifier
   (REQ-0628).
4. It fails a fixture draft epic with a status per task (REQ-2897).
5. Every requirement ADR-2590 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [ ] T-001 [P] TSK-4770 fail a record that declares `status: live`, a specification that carries history and a withdrawal that names nothing, in the `record` feature of `crates/meow/`
      closes: REQ-0610, REQ-0612, REQ-0628, REQ-0632

- [ ] T-002 [P] TSK-4780 derive a task's state from the task and drop the per-task mark from a draft epic, in `crates/meow/` and the epic template
      closes: REQ-2897

## Coverage

Each of the five requirements ADR-2590 addresses lands in exactly one task.
TSK-4780 alone tests the amendment to ADR-2300, because it moves where a
task's state is read. The two tasks run in parallel.

## Not covered

Migrating approved epics that carry a mark per task, which ADR-2590 excuses
under method rule M15: they keep their marks, and `paw` reads both forms.
