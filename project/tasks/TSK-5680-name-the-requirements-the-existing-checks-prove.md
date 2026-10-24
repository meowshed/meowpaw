---
id: TSK-5680
artifact: task
status: approved
revised: 2026-10-24
epic: EPC-2850
closes: [REQ-4610, REQ-4612, REQ-4614, REQ-3074]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Name the requirements the existing checks prove

Four requirements already hold, and no test cites them. This task adds the tests that fail if each stops holding, and cites the requirement in each.

## Acceptance criteria

1. Given the Rust build, the release workflows and every launcher, when a test reads them, then each names the executable `paw` and none names `meow-<target>` for the shared executable, and the Windows launcher path ends in `.exe` (REQ-4610). Closed by: a test naming REQ-4610 in `tools/test_shared_binary.py`, seen failing against a launcher edited to another name.
2. Given the core unit's build and the Pi core extension, when a test reads them, then the core build compiles every feature, the Pi extension exports `MEOWPAW_BINARY`, and no other unit's launcher resolves its own wrapper (REQ-4612). Closed by: a test naming REQ-4612.
3. Given every unit that ships a Claude plugin and a Pi package, when a test reads the two manifests, then each pair carries the same version, and a pair that differs fails the test naming the unit (REQ-4614). Closed by: a test naming REQ-4614, seen failing against a package version edited by one patch.
4. Given this repository's trunk, when `mise run all` runs, then it exits 0 and `paw check` reports no finding (REQ-3074). Closed by: the gate of the pull request that carries this task.

## What to do

Read `tools/test_shared_binary.py`, `tools/test_release_layout.py`, `tools/test_pi_extensions.py` and `tools/check_release.py` first: where a test already proves a criterion, name the requirement in its docstring and add nothing, and where none does, write it. The same-pull-request rule in REQ-4614 rests on review and is named so in the Evidence.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

A change to any launcher, which TSK-5683 and TSK-5684 make.
