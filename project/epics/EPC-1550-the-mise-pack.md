---
id: EPC-1550
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1580
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

## Coverage

ADR-1580 addresses 23 requirements, and each lands in exactly one task above.
T-002 and T-003 both build on T-001's program and touch different commands,
so they can run side by side once T-001 lands.

## Not covered

The ten requirements ADR-1580 postpones: REQ-2480, REQ-2486, REQ-2487,
REQ-2488, REQ-2508 and REQ-2510 until the go-task pack, REQ-2494 and REQ-2498
until the make pack, REQ-2484 until the first language pack, and REQ-2502
until a pack writes a tool version.
