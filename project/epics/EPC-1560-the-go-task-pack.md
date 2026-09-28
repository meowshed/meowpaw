---
id: EPC-1560
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1590
checked-at: "#587"
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

## Verified

I checked this under #587 on `main` after #594, gathering the evidence there
rather than carrying it over from the tasks. `meow-verbs evidence --keep
format lint test` exits 0 on this change's own tree, each result kept in
`project/evidence/`, as the pull request cites. The 29 fixtures in
`plugins/meow-gotask/tests/test_gotask.py` run 29, OK, against Task 3.53.1,
and `meow-mise`'s 38 run 38, OK, against the shared module. Every criterion is
met:

| Criterion                                                                                                                                | Evidence on `main` after #594                                                                                                                         |
| ---------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. `status` reports each block, a dependency's block through it, a namespaced task and what decides a skip                               | The 13 fixtures in the `Status` class pass                                                                                                            |
| 2. Listing leaves the tree alone, and a task with `sources` runs afterwards                                                              | `Status.test_listing_leaves_the_tree_and_freshness_alone` passes, and fails against a program that lists without moving `TASK_TEMP_DIR`               |
| 3. A remote include is named and nothing listed, `check` finds it, and 104 or 106 is reported as a remote Taskfile the listing can't see | The two `Remote` fixtures, `Check.test_a_remote_include_is_a_finding`, and `Unresolved.test_104_is_never_untrusted` and `test_106_is_unresolved` pass |
| 4. A secret variable is named as masked and never shown                                                                                  | `Status.test_a_secret_is_named_as_masked_and_never_shown` passes                                                                                      |
| 5. `bind` binds with `--force`, and `check` finds a skippable task run without it                                                        | The two `Bind` fixtures and `Check.test_a_skippable_task_without_force_is_a_finding` pass                                                             |
| 6. `check` reports hand-written bindings with their blocks, and `status` blocks `if` and `platforms`                                     | `Check.test_hand_written_bindings_report_their_blocks_never_missing` and `Status.test_if_and_platforms_are_blocks` pass                               |
| 7. Every requirement lands in one closed task, and REQ-2488 reads as postponed                                                           | `paw show` derives REQ-2480, REQ-2486, REQ-2487, REQ-2508 and REQ-2510 as closed by TSK-2450 or TSK-2460, and REQ-2488 as postponed                   |

### Documentation

`plugins/meow-gotask/README.md` describes the three commands and every
unresolved line, and the documentation index lists the unit. The `test` verb
checked the pages.

### Postponements

REQ-2488 stays postponed until a program running Task can see a changed
checksum; the condition doesn't hold on Task 3.53.1.

## Coverage

ADR-1590 addresses 5 requirements, and each lands in exactly one task above.
T-002 builds on T-001's program, so they run in order.

## Not covered

REQ-2488, which ADR-1590 postpones until a program running Task can see a
changed checksum.
