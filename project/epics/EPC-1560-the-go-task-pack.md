---
id: EPC-1560
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1590
---

# A go-task pack reads a Taskfile without writing to it, and binds a verb only to a task that can run unattended

Realises exactly one authorising record, ADR-1590. The epic is complete when
`meow-gotask` ships with `status`, `bind` and `check`, each reporting what
ADR-1590 decides, held by fixtures that run real Task.

## Acceptance criteria

Taken from ADR-1590, from its list of how I will know it was realised, before
the tasks below were written:

1. Fixtures with real Task show `status` reporting a committed task with no
   block, and an internal, a prompting, a variable-requiring and an
   error-ignoring task each with its block, and a task depending on the
   error-ignoring one blocked through it. They also show a task from an
   include with its namespace, and a task that can skip with what decides it.
2. A fixture lists a Taskfile whose task declares `sources`, then runs that
   task with Task, and the task runs; `git status --porcelain --ignored`
   reads as before after all three commands.
3. A fixture with a remote include shows the include named, the report
   unresolved for it with exit status 3, and no listing run; `check` reports
   the include as a finding. A stand-in Task exiting 104 or 106 is reported as
   untrusted or not cached.
4. A fixture shows a `secret: true` variable named as masked and not
   protected, with its value absent from the output.
5. Fixtures show `bind` binding `test` as `task --force test` and leaving a
   blocked task unbound with its reason, and `check` exiting 1 on a skippable
   task run without `--force`.
6. Fixtures show `check` reporting a hand-written binding to an internal, a
   prompting and a variable-requiring task, each with its block and none as
   missing, and `status` blocking an `if` and a `platforms` task.
7. Every requirement ADR-1590 addresses lands in exactly one closed task, and
   REQ-2488 reads as postponed.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2450 ship the unit and `status`, sharing the runner code with
      `meow-mise`
      closes: REQ-2480, REQ-2486, REQ-2508, REQ-2510
      evidence: 22 fixtures seen failing first, against real Task, and
      `meow-mise`'s 38 unchanged, in #589.

- [x] T-002 TSK-2460 bind the verbs and check the profile and the includes
      closes: REQ-2487
      evidence: 7 fixtures, 6 seen failing first, in #590.

## Coverage

ADR-1590 addresses 5 requirements, and each lands in exactly one task above.
T-002 builds on T-001's program, so they run in order.

## Not covered

REQ-2488, which ADR-1590 postpones until a program running Task can see a
changed checksum.
