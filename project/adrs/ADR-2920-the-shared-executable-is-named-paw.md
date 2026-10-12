---
id: ADR-2920
artifact: adr
status: done
revised: 2026-10-11
addresses: [REQ-4610, REQ-4612, REQ-4614, REQ-4500, REQ-4504]
supersedes: [ADR-1350, ADR-2810, ADR-2820, ADR-2870]
---

# 2920. The shared executable is named `paw`

## Decision

The shared native executable is named `paw` in the Claude Code plugins and Pi
packages. Rust's crate remains `meow`, and unit, package and subcommand names
remain unchanged. The core unit ships the one all-features executable; Claude
launchers locate it through the core data marker, and Pi's core extension sets
`MEOWPAW_BINARY` to its absolute path so another package's `bin/paw` launcher
cannot recursively resolve itself from `PATH`.

Every unit's Claude plugin and Pi package remains aligned in the same pull
request: shared skills, behavior, public contract and documentation change on
both sides, and both manifests carry one version. Host-specific adapters stay
in their respective distribution. A unit tag releases both distributions.

This changes the executable-name clause of ADR-1350 and ADR-2810, and the
executable-name and cross-platform maintenance clauses of ADR-2820 and
ADR-2870. Their other decisions remain in force. Once this record is accepted,
the Rust build, installers, launchers, workflows, documentation and release
artifacts use `paw` as the executable filename. What still doesn't work: a
previously installed Pi package that only has a `meow` executable must be
upgraded to a release carrying `paw`.

## Why

The owner asked for one command name across the two plugin distributions. The
existing command `paw` already names record operations, while `meow` names the
crate and units. Using `paw` for the shared executable makes shell invocation
and shipped filename agree, and parallel updates prevent a unit's Claude and
Pi versions from naming different behavior.

## Alternatives

| Option                                           | Better at              | Why it lost                                                           |
| ------------------------------------------------ | ---------------------- | --------------------------------------------------------------------- |
| Keep the executable named `meow`                 | No rename              | The owner explicitly chose `paw` for both distributions               |
| Rename the crate and every unit to `paw`         | One product name       | Unnecessary crate and package churn; only the executable name changes |
| Keep different executable names on Claude and Pi | Fits existing archives | Preserves the cross-platform drift the shared contract should remove  |

## What it costs

All release artifacts and launchers must agree on `paw`, and every unit release
must advance both manifests in lockstep. Pi launchers must use the core
extension's absolute executable path to avoid finding a package's own `bin/paw`
wrapper on `PATH`.

## What would reverse it

- A platform requirement prevents either distribution from shipping or running
  an executable named `paw`.

## Consequences

The Rust crate keeps its established package name, while each built artifact
ships as `paw`. Pi packages resolve the executable through one absolute path,
and every shared unit version names the same Claude and Pi content.

## How you will know

1. The Rust build emits `paw` for every supported target.
2. Claude and Pi package launchers invoke the shared `paw` executable, and Pi
   launchers use `MEOWPAW_BINARY` when the core extension has set it.
3. The package and plugin versions agree for every unit, and shared skill
   contents match across the two distributions.
4. A unit tag starts both release workflows.

## What this does not settle

- Renaming crate, package, unit, or subcommand names, which remain `meow`.
