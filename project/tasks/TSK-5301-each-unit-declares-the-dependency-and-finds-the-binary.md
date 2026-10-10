---
id: TSK-5301
artifact: task
status: approved
revised: 2026-10-10
epic: EPC-2780
closes: [REQ-4502, REQ-4504, REQ-4506, REQ-4508]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Each unit declares the dependency and finds the binary

Each unit that runs a program names `meow-core` under `dependencies`, and its
launcher reads the data file before it looks beside itself.

## Acceptance criteria

1. Given each unit's manifest, when `.claude-plugin/plugin.json` is read, then a
   unit with a launcher lists `meow-core` and no other unit under `dependencies`.
   Closed by: a test in `tools/`.
2. Given the data file naming a root with a binary, when a launcher runs, then it
   runs that binary. Closed by: a test of the launcher in each unit's tests.
3. Given no data file, when a launcher runs, then it exits 3 and names
   `meow-core`. Closed by: a test of the launcher in each unit's tests.
4. Given each unit's manifest, when `.claude-plugin/plugin.json` is read, then it
   carries its own `version`, and a `dependencies` entry carries no range tied to
   another unit's version. Closed by: a test in `tools/` (REQ-4508).

## What to do

Change the 13 launchers and the manifests, and keep the lookup beside the unit
as the fallback until EPC-2790 removes the builds.

## Depends on

- TSK-5300 (blocking): a launcher needs the data file to read.

## Evidence

Not yet.

## Left alone

The release, which EPC-2790 changes.
