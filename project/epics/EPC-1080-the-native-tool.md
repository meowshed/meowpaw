---
id: EPC-1080
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1110
checked-at:
---

# One native tool for every unit's program

Realises exactly one authorising record, ADR-1110. The epic is complete when
every unit's program is a subcommand of `meow`, each unit ships a binary built
with its own feature for six targets, the Python programs are gone, and a
release publishes each unit as a pinned archive.

## Acceptance criteria

Taken from ADR-1110, from its list of how I will know it was realised, before
the tasks below were written:

1. The fixtures of `meow-verbs`, `meow-scm` and `meow-git`, unchanged, pass
   against launchers that run the Rust binary.
2. The crate builds for all six targets in continuous integration.
3. A unit installed from a published archive runs on a machine with neither
   Python nor Node.js.
4. On a machine with no binary for its target, the launcher reports every
   check as unrun, and nothing passes.
5. No binary is in the repository's history, and the Python programs are gone.
6. The size of each unit's archive is published with the release.
7. Every requirement ADR-1110 addresses lands in exactly one closed task, and
   the checks over the record report nothing outstanding.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [ ] T-001 TSK-1350 the crate, the shared profile and report module, the local
      build, and `meow verbs` ported with its launcher
      closes: REQ-0032, REQ-0076

- [ ] T-002 TSK-1360 `meow scm` ported with its launcher
      depends: TSK-1350 - it builds on the crate and the shared module

- [ ] T-003 TSK-1370 `meow git` ported with its launcher
      depends: TSK-1350 - it builds on the crate and the shared module

- [ ] T-004 TSK-1380 the release: six targets, an archive per unit, the
      marketplace file, and each archive's size published
      closes: REQ-0074, REQ-3178
      depends: TSK-1350, TSK-1360, TSK-1370 - a release carries every ported
      unit

## Coverage

ADR-1110 addresses four requirements. Each lands in exactly one task above,
and `tools/check_coverage.py` compares the decision's `addresses` against the
union of the tasks' `closes`.

T-001 alone tests the decision locally: one unit running on the native binary
with its fixtures unchanged. T-004 is where a person without Rust gets it.

## Not covered

The record checks are built in the crate by TSK-1330 of EPC-1070, amended to
depend on T-001. Signing the binaries is outside this epic, as ADR-1110 says.
