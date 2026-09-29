---
id: BUG-1341
artifact: bug
status: approved
severity: major
violates: REQ-2392
enters: implement
found: 2026-09-29
revised: 2026-09-29
issue: 682
---

# `meow-unattended plan` prints each unit as a path relative to the root, which names nothing from a subdirectory

`plan` prints `--plugin-dir` with each `units` entry exactly as the profile
wrote it, relative, and records the same relative `path` in the snapshot. It
checks the entry against the repository root, but it finds that root from any
subdirectory and never says the command has to run there, so the printed
command can name a directory that doesn't exist.

## Reproduction

`main` after #675, with `meow-unattended` 0.2.1 built by
`crates/meow/build-units`.

1. In a scratch git repository, declare `[git] trunk = "main"` and an
   `[unattended]` table with `permission_mode = "dontAsk"`, `budget_usd = 1`,
   `gates = []` and `units = ["units/alpha"]`, and give `units/alpha` a
   `.claude-plugin/plugin.json`.
2. Create a directory `sub` and run `meow-unattended plan` in it.

## What the system does

`plan` exits 0, prints `--plugin-dir units/alpha`, and writes
`"path": "units/alpha"` into the snapshot. Run from `sub`, that argument names
`sub/units/alpha`, which doesn't exist. `plan` in
`crates/meow/src/unattended.rs` passes `unit.entry` to the command line and
the snapshot, while `unit()` reads `root.join(&entry)`.

## What it should do, and why

Each `--plugin-dir` names the unit's own directory wherever the command runs,
so the run loads the units the plan checked, which is what REQ-2392 asks.
SPC-1200 says each path in `units` resolves against the work tree's root, and
the printed command is where that resolution has to reach. A unit that fails
to load doesn't stop the run: RES-0299 reports that `--plugin-dir` failures
land in `plugin_errors` and the run goes on, so the run would start without
the harness it names.

I haven't started a run, so I haven't seen what Claude Code 2.1.283 does with
this argument; the defect is that the printed command names a directory that
isn't the unit's, whatever Claude Code does next.

## Triage

It enters at implement, because REQ-2392, ADR-2000 and SPC-1200 are right and
the program prints the entry before resolving it. Major, because the plan
says it loads a unit by name and hands over a command that, from a
subdirectory, loads none.

## Closed by

The reproduction as a fixture in
`plugins/meow-unattended/tests/test_unattended.py`,
`Units.test_unit_paths_hold_from_a_subdirectory`, which runs `plan` in a
subdirectory and needs every `--plugin-dir` and every snapshot `path` to be
absolute and to name the declared unit's directory.

## Tasks

- [x] T-001 TSK-3330 print and record each unit as its absolute path, in
      `crates/meow/src/unattended.rs`
      evidence: 1 check seen failing first, 19 `meow-unattended` fixtures
      passing, in #683.
