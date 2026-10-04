---
id: ADR-2800
artifact: adr
status: done
revised: 2026-10-04
addresses: [REQ-4140, REQ-4142]
supersedes: []
---

# 2800. The packages publish to npm, and every target builds under Linux

## Decision

The six meowpaw Pi packages publish to npm under the `@meowshed` scope, and
each tarball carries the meow-full binary for every platform the build
workflow builds. An install is:

```bash
pi install npm:@meowshed/meow-core
```

and needs no checkout, no download and no network at load: the tarball is
the whole package, binaries included. The `postinstall` stays and runs for
a git-source install, where the clone obeys `.gitignore` and the platform
directories are absent; under npm the same script is a no-op, because it
finds the binary already present and exits 0.

A local-path install remains a development install: it tracks the checkout,
runs nothing at install time, and the person installing that way runs
`node install-meow.mjs` by hand. It is documented as development, not
distribution.

The release workflow packs each package from the build workflow's
artifacts — placing all six platforms in `bin/` before `npm pack` — and
publishes to npm with `--provenance` under a token held in the
`NPM_TOKEN` secret. The GitHub releases of the package archives stay, as
the record of what shipped and as the download source the installer names.

The build workflow runs no macOS and no Windows runner. All six targets
build under Linux: the musl targets natively, the windows targets through
cargo-xwin, which fetches the Windows SDK from Microsoft's own servers,
and the darwin targets through osxcross in a container, whose image
carries the macOS SDK and is named and pinned in the workflow. Every
darwin binary is signed with `ldid` before packing and signed again by the
installer with `codesign` after download, because the macOS kernel kills
an unsigned arm64 binary on sight. The Claude Code marketplace release
calls the same build and keeps its per-unit archives carrying all six
platforms.

## Why

RES-0342 found that a local-path install is a pointer into the checkout and
runs no lifecycle script, so the install dies with the checkout and the
binaries had to be fetched by hand — the two gaps the first install showed.
The pi-release workflow already builds and packs everything the npm route
needs; publishing adds one step and makes the person's install one command
that works on any machine.

The tarball carrying the binaries removes the last network step from an
install. A download at install time would work — the installer already
implements one — but an install that fetches nothing cannot fail to fetch,
and the wrapper's unrun report then covers only a genuinely broken
environment.

The build change removes the macOS and Windows runners because each adds
minutes of queue and a runner family the repository pays for, where a
cross-compile from Linux builds the same six binaries in one job family.
The trade-off is the darwin SDK's licence on Linux, named in RES-0343 and
pinned in the workflow, and the container image it rides on, which becomes
a supply-chain dependency to watch.

## Alternatives

| Option                                        | Better at                                                  | Why it lost                                                                                                                                                    |
| --------------------------------------------- | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| npm tarball carrying all six binaries         | One command, no download, works everywhere                 | Chosen                                                                                                                                                         |
| npm tarball with `postinstall` downloading    | Tarball of 1 MB instead of 8                               | A download in the install path that can fail for a network reason, where the binary is a static file the release already holds                                 |
| One aggregate package at the repository root  | `pi install git:...` works with no npm account             | Installs all six layers at once and loses the install-only-what-you-need property; a root package.json also makes the meowpaw repository itself an npm package |
| GitHub release archives as the install source | No npm account needed                                      | Pi has no install source for an archive URL; the marketplace mechanism that consumes one is Claude Code's, not Pi's                                            |
| Keep the macOS and Windows runners            | The darwin SDK stays on Apple hardware, inside its licence | Six runners to maintain and pay for, where three Linux jobs build the same binaries; the trade-off is named, pinned and reversible                             |

## What it costs

Each npm tarball is roughly 8 MB, six platforms of a stripped binary plus
the package's own files. Publishing needs an npm account with the
`@meowshed` scope and a token in the repository's `NPM_TOKEN` secret;
until that token exists, the packages install from a local path or a git
source. The `@meowshed` scope is reserved the day the first package
publishes.

The darwin SDK on Linux sits outside Apple's licence, and the container
image that carries it is a third-party dependency the supply chain has to
trust; both are named in the workflow and in RES-0343. The cross-built
darwin binaries are exercised by no macOS runner, so a darwin-only defect
that a Linux build cannot show would surface first on a person's machine —
the installer's unrun report and the wrapper's exit statuses are what
catch it.

## What would reverse it

- npm removes or breaks scoped publishing with provenance, and a
  different registry or distribution channel is chosen.
- The tarball size grows past what npm tolerates or what a person accepts
  downloading, and the binaries return to a `postinstall` download.
- Pi ships a first-class marketplace or archive install source, and the
  packages move to it.
- A darwin or windows binary built under Linux shows a defect the old
  runners' builds did not have, and the cost of that surfaces more than
  once; the runners return.

## Consequences

- An install is one command per package, from any machine, with no
  checkout: `pi install npm:@meowshed/<unit>`.
- The `postinstall` runs for a git source and no-ops under npm.
- The release workflow publishes to npm only where `NPM_TOKEN` is set;
  the packing and the GitHub releases run regardless.
- A local-path install is documented as development-only.
- The meow-full GitHub release remains the installer's download source for
  a git install.

## How I will know it was realised

1. `npm pack --dry-run` in each package lists `bin/<triple>/meow` for all
   six platforms.
2. `pi install npm:@meowshed/meow-core` succeeds on a machine with no
   meowpaw checkout, and a Pi session from it quotes the reply shape.
3. The `postinstall` in an npm install leaves no archive and makes no
   request, because the binary is already present.
4. The workflow run's publish step reports six packages published with
   provenance.
5. A workflow run on the new build jobs produces the `bin-<target>`
   artifacts for all six targets from Linux runners, and the marketplace
   release packs its per-unit archives from them.
6. A darwin binary from that run carries an ad-hoc signature, and a Pi
   session on this machine runs it.

## What this does not settle

- The npm account and the token, which a person holds and sets once.
- Whether the packs ship to npm before the layers do.
- Whether a future Pi version ships its own distribution channel.
- Which community image carries the darwin SDK, beyond the one pinned
  today, and whether a self-built osxcross replaces it.
