---
id: TSK-5302
artifact: task
status: done
revised: 2026-10-10
epic: EPC-2790
closes: [REQ-4500]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The release packs one build and the units ship none

The release workflow packs the binary into `meow-core` only, and the other
units' archives hold no `bin/<target>` directory.

## Acceptance criteria

1. Given a pack-only run of the release workflow, when it finishes, then only the
   `meow-core` archive holds a platform binary. Closed by: a test in `tools/`.
2. Given a built tree, when `build-units` finishes, then no unit but
   `meow-core` has a `bin/<target>` directory. Closed by: a test in `tools/`.

## What to do

Change `crates/meow/build-units` and `.github/workflows/claude-release.yml`.

## Depends on

- EPC-2780 (blocking): the launchers find the shared binary first.

## Evidence

Pull request 881. The tests are `tools/test_release_layout.py` and
`tools/test_launchers.py`:

- Criterion 1: the artifact-path test, where the build fills one unit.
- Criterion 2: the test that the build script has no loop over the units' own
  builds.

A unit loaded in place finds `plugins/meow-core` beside it with no data file,
which `test_launchers.py` also tests.

## Left alone

The Pi release, which already ships one build.
