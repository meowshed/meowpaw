---
id: EPC-2340
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2480
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Each unit is a versioned plugin, held by checks to its manifest and its release

Realises exactly one authorising record, ADR-2480. The epic is complete when
each unit's `requires.toml` states its layer, the units it needs and, in a
pack, the kernel range, `meow-author check` fails a unit missing any of them,
the release refuses a changed unit at a released version and a version with
no written notes, a launcher stops on an older platform, and tests hold the
rest of the contract, as SPC-1080 states under "Each unit is a plugin".

## Acceptance criteria

Taken from ADR-2480's list of how it will be known realised:

1. `meow-author check` fails a fixture unit with no `requires.toml`
   (REQ-1482).
2. The release exits non-zero for a unit whose files changed since its tag
   while its version equals the tag's (REQ-2996).
3. A unit run under a lower platform version than it names prints both
   versions and stops (REQ-1738).
4. No file under a unit's install root is written at run time (REQ-3000).
5. Every requirement ADR-2480 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [ ] T-001 TSK-4390 state each unit's layer, required units and kernel range in `requires.toml`, and fail a unit missing one in `meow-author check`
      closes: REQ-1482, REQ-2990, REQ-2998, REQ-3006

- [ ] T-002 [P] TSK-4400 refuse a changed unit at a released version and a version with no written notes, in the release
      closes: REQ-2996, REQ-3002

- [ ] T-003 [P] TSK-4410 stop a launcher on a platform older than its unit's `claude_code`
      closes: REQ-1738

- [ ] T-004 [P] TSK-4420 hold the rest of the plugin contract with tests: the install, the contracts between units, the install root and the configuration format
      closes: REQ-1480, REQ-1481, REQ-1483, REQ-1484, REQ-1488, REQ-1494, REQ-2994, REQ-3000

## Coverage

Each of the fifteen requirements ADR-2480 addresses lands in exactly one
task. TSK-4390 and TSK-4400 together test the decision, because the manifest
and the release are where a unit's version and its dependencies are either
held or not. The four tasks touch different files and run in parallel.

## Not covered

What the public interface is, which ADR-2490 declares, and provisioning
without a person, which ADR-2500 decides, because ADR-2480 leaves both to
those decisions.

ADR-2480's second criterion reads "the release workflow exits non-zero for a
version whose tag exists". Read literally, that conflicts with SPC-1080, where
the release keeps the archive of every unchanged unit whose version already
has a release, so every ordinary release would fail. I took it as the case
REQ-2996 forbids, a unit changed under a released version, and criterion 2 says so.
