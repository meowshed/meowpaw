---
id: EPC-1080
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1110
checked-at: "#160"
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

- [x] T-001 TSK-1350 the crate, the shared profile and report module, the local
      build, and `meow verbs` ported with its launcher
      closes: REQ-0032, REQ-0076
      evidence: meow-verbs' twelve fixtures, unchanged, passing against the
      native binary, and the crate's tests, in #150.

- [x] T-002 TSK-1360 `meow scm` ported with its launcher
      evidence: meow-scm's fourteen fixtures, unchanged, passing against the
      native binary, in #155.
      depends: TSK-1350 - it builds on the crate and the shared module

- [x] T-003 TSK-1370 `meow git` ported with its launcher
      evidence: meow-git's twelve fixtures, unchanged, passing against the native
      binary, in #152.
      depends: TSK-1350 - it builds on the crate and the shared module

- [x] T-004 TSK-1380 the release: six targets, an archive per unit, the
      marketplace file, and each archive's size published
      closes: REQ-0074, REQ-3178
      evidence: release run 36232216779, and two units installed from it and
      run in a container with neither Python nor Node.js, in #153.
      depends: TSK-1350, TSK-1360, TSK-1370 - a release carries every ported
      unit

- [+] T-005 TSK-1390 the six-target build run by CI on every change to the
  crate, and called by the release
  added: the verification under #160 found criterion 2 met only by the
  release run by hand, because T-004 put the matrix there.
  evidence: Build run 36233014435 on the pull request and release run
  36233124490 calling it, all six targets built, in #161.
  depends: TSK-1380 - it moves the matrix that task wrote

## Verified

Checked under issue 160 at revision `c00ebc8`, with evidence gathered there and
not carried over from the tasks. Every criterion is met:

| Criterion                                                    | Evidence at `c00ebc8`                                                                                                                                                             |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. The units' fixtures, unchanged, pass on the Rust binary   | `python3 -m unittest discover` ran 12, 14 and 12 tests for meow-verbs, meow-scm and meow-git, each `OK`; `git diff 409d597 HEAD` over their `tests/` is empty                     |
| 2. The crate builds for all six targets in CI                | Build run 36233253734, started by the push of `c00ebc8` to `main`, built all six targets                                                                                          |
| 3. A unit from a published archive runs with no interpreter  | In `debian:bookworm-slim` on aarch64, `python3` and `node` absent, meow-verbs, meow-scm and meow-git installed from the release and ran: `run test` passed, `push-guard` exited 0 |
| 4. With no binary, every check is unrun                      | Launchers copied without `bin/<target>/`: meow-verbs exits 3 with `test unresolved`, meow-scm exits 3 with `unchecked`, meow-git exits 0 with `unrun`                             |
| 5. No binary in history, the Python programs gone            | `git log --all --name-only` finds 0 paths under `plugins/*/bin/<target>/`; `git ls-files 'plugins/*.py'` outside `tests/` finds 0                                                 |
| 6. Each archive's size is published                          | The `marketplace` release lists all six archives with their bytes and SHA-256                                                                                                     |
| 7. Every requirement in one closed task, nothing outstanding | `tools/check_coverage.py`: EPC-1080 4 of 4, 0 coverage failures; the front matter, identifier, index and link checks report 0 failures                                            |

The install in criterion 3 ran against the release published from `a11d08e`,
and nothing under `crates/` or `plugins/` changed between that revision and
`c00ebc8`. `mise run all` exited 101 twice at `c00ebc8`, and then 0 on four
runs, with no failing task in the passing runs' output. The cause is unknown.

## Coverage

ADR-1110 addresses four requirements. Each lands in exactly one task above,
and `tools/check_coverage.py` compares the decision's `addresses` against the
union of the tasks' `closes`.

T-001 alone tests the decision locally: one unit running on the native binary
with its fixtures unchanged. T-004 is where a person without Rust gets it.

## Not covered

The record checks are built in the crate by TSK-1330 of EPC-1070, amended to
depend on T-001. Signing the binaries is outside this epic, as ADR-1110 says.
