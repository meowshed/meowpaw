---
id: EPC-1550
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1580
checked-at: "#577"
---

# A mise pack reads the tasks a repository declares, and binds a verb only to a task that can run unattended

Realises exactly one authorising record, ADR-1580. The epic is complete when
`meow-mise` ships with `status`, `bind` and `check`, each reporting what
ADR-1580 decides, held by fixtures that run real mise.

## Acceptance criteria

Taken from ADR-1580, from its list of how I will know it was realised, before
the tasks below were written:

1. Fixtures with real mise show `status` on a repository with a committed
   task, a hidden one, a confirm one, one taking a required argument, one
   with `sources` and `outputs`, a file task, a parent directory's task and a
   `mise.local.toml` replacing a committed task, each reported as ADR-1580
   says.
2. A fixture with an untrusted template shows `untrusted` with exit status 3,
   and `mise trust --show` still reports the directory untrusted afterwards.
3. Fixtures with a stand-in mise show an unrecognised listing and an
   `unexpected argument` each reported as unresolved with exit status 3,
   never as an empty list.
4. A fixture shows `bind` binding `test` to `mise run --force test`, binding
   nothing to a near name, and leaving each blocked task unbound with its
   reason; another shows the work tree unchanged after all three commands.
5. A fixture shows `check` exiting 1 on a verb that runs a skippable task
   without `--force`, and 0 on this repository's profile.
6. Every requirement ADR-1580 addresses lands in exactly one closed task, and
   the ten it postpones read as postponed.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2420 ship the unit and `status`'s task listing
      closes: REQ-2460, REQ-2462, REQ-2464, REQ-2465, REQ-2466, REQ-2467,
      REQ-2470, REQ-2472, REQ-2473, REQ-2476, REQ-2478, REQ-2479, REQ-2496,
      REQ-2500
      evidence: 21 fixtures, 20 seen failing first, most against real mise,
      in #579.

- [x] T-002 [P] TSK-2430 report the pinned tools, the environment's files and
      idiomatic version files
      closes: REQ-2482, REQ-2490, REQ-2506
      evidence: five fixtures seen failing first, against real mise, in #580.

- [x] T-003 [P] TSK-2440 bind the verbs and check the profile's bindings
      closes: REQ-1316, REQ-2354, REQ-2468, REQ-2474, REQ-2492, REQ-2504
      evidence: 12 fixtures, 11 seen failing first, and `check` passing on
      this repository's profile, in #581.

## Verified

I checked this under #577 on `main` after #584, gathering the evidence there
rather than carrying it over from the tasks. `meow-verbs evidence --keep
format lint test` exits 0 on this change's own tree, each result kept in
`project/evidence/`, as the pull request cites. The 38 fixtures in
`plugins/meow-mise/tests/test_mise.py` run 38, OK, against mise 2026.9.11.
`meow-mise check` on this repository prints `0 findings in 7 task runs the
profile's verbs name` and exits 0. Every criterion is met:

| Criterion                                                                                                                    | Evidence on `main` after #584                                                                                                                                                                                                              |
| ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1. `status` reports each kind of task as decided                                                                             | The 11 fixtures in the `Status` class pass: a committed task with no block, hidden, confirm as a TOML key and a file task header, a required argument, a task that can skip, a parent directory's task and a `mise.local.toml` replacement |
| 2. An untrusted template is `untrusted` with exit status 3 and stays untrusted                                               | `Trust.test_an_untrusted_template_is_unresolved_and_stays_untrusted` passes                                                                                                                                                                |
| 3. A stand-in's unrecognised listing and `unexpected argument` are unresolved with exit status 3                             | The four stand-in fixtures in `Unresolved` pass, among them `test_an_unrecognised_listing_is_never_empty` and `test_an_older_mise_is_an_environment_failure`                                                                               |
| 4. `bind` binds `test` with `--force`, nothing to a near name, and leaves blocked tasks unbound; no command changes the tree | The four fixtures in `Bind` and `WritesNothing.test_no_command_changes_the_tree` pass                                                                                                                                                      |
| 5. `check` exits 1 on a skippable task without `--force`, and 0 on this repository                                           | `Check.test_a_skippable_task_without_force_is_a_finding` and `Check.test_this_repositorys_profile_is_clean` pass, and the `lint` verb runs `check`                                                                                         |
| 6. Every requirement lands in exactly one closed task, and the ten postponed read as postponed                               | `paw show` derives each of the 23 as closed by one of TSK-2420, TSK-2430 and TSK-2440, and the ten as postponed by ADR-1580                                                                                                                |

### Documentation

`plugins/meow-mise/README.md` describes the three commands and every
unresolved line, and the documentation index lists the unit. The `test` verb
checked the pages, running `tools/check_docs.py`.

### Postponements

ADR-1580 postpones six requirements until the go-task pack, two until the make
pack, REQ-2484 until the first language pack and REQ-2502 until a pack writes a
tool version. None of those conditions holds today. The owner decides whether
any does.

## Coverage

ADR-1580 addresses 23 requirements, and each lands in exactly one task above.
T-002 and T-003 both build on T-001's program and touch different commands,
so they can run side by side once T-001 lands.

## Not covered

The ten requirements ADR-1580 postpones: REQ-2480, REQ-2486, REQ-2487,
REQ-2488, REQ-2508 and REQ-2510 until the go-task pack, REQ-2494 and REQ-2498
until the make pack, REQ-2484 until the first language pack, and REQ-2502
until a pack writes a tool version.
