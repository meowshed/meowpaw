---
id: ADR-2810
artifact: adr
status: done
revised: 2026-10-04
addresses: [REQ-4142, REQ-4144]
supersedes: []
---

# 2810. The Rust tool builds in its own workflow, and the meow binary ships with the core package alone

## Decision

The build splits into three workflows, and the meow binary ships with the
core Pi package and no other.

1. **`rust-tool.yml` builds and publishes the native tool alone.** It runs
   when a push to the trunk changes `crates/**` or the workflow itself, by
   hand, or on a `meow-full-v<version>` tag. It builds the per-unit
   binaries for the Claude Code marketplace and the all-features binary for
   the Pi packages, uploads them as artifacts, and publishes the meow-full
   release. A change to plugin files alone never builds Rust.

2. **`claude-release.yml` releases the Claude Code units without building.**
   It fetches the `bin-<target>` artifacts from the latest successful
   `rust-tool` run on the trunk, packs each unit's archive, and updates the
   marketplace. Where a unit already has a release, its own archive is
   reused as before. Where the artifacts are gone, it fails and names the
   workflow to run.

3. **`pi-release.yml` releases the Pi packages without building.** It
   fetches the `full-<target>` artifacts the same way, places the six
   platform binaries into `meow-core` alone, and publishes to npm. The
   other five packages carry no binary at all.

4. **The meow binary ships with the core package and only with it.** The
   core tarball carries the all-features binary for all six platforms; the
   core extension puts the binary's own directory on PATH. Every other
   package's launcher looks for its unit's binary beside itself first and
   falls back to `meow` on PATH, so a wrapper runs through the core
   package's binary wherever the core package is installed, and reports
   unrun where it is not.

## Why

A plugin release that rebuilds thirteen feature binaries for six targets
waits ten minutes for an hour of no change: the binaries are content of
`crates/**`, and a release that touches only plugin files cannot change
them. The artifacts of a run that did build are exactly current for the
crate state the trunk holds, because only a crate change starts the build.
The meow binary in five packages is five redundant copies of 8 MB and five
installers where one distribution point serves them: the core package is
the layer every other layer installs beside, and its extension is already
the one that puts the wrappers' directory on PATH.

## Alternatives

| Option                                                    | Better at                              | Why it lost                                                                                                                                                        |
| --------------------------------------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Three workflows, artifacts fetched from the last Rust run | Plugin releases start in seconds       | Chosen                                                                                                                                                             |
| One workflow, build job gated by a paths check            | Fewer files                            | The plugin jobs still declare the build as a dependency, and a skipped build leaves the release job reading an empty artifact set it cannot tell from a broken one |
| Every package keeps its own binary                        | A package works beside no core install | Five copies of the same 2 MB per platform, five installers, and a version to keep in step                                                                          |
| Claude Code units also switch to the shared full binary   | One binary everywhere                  | The marketplace units ship their own feature's code and nothing of another unit's, which is the released contract; changing it is a release of its own             |

## What it costs

A plugin release depends on a successful Rust run existing on the trunk,
and its artifacts surviving: where none exists, the release fails and
names `rust-tool.yml`. The artifact store holds both artifact families
until their retention ends. A Pi package without the core package
installed resolves its wrapper to unrun, which the wrapper already reports
as designed.

## What would reverse it

- Pi adds a first-class way for one package to depend on another's files,
  and the wrappers resolve through it instead of PATH.
- The Claude Code units adopt the shared all-features binary, and the
  per-unit builds retire.
- Artifact retention proves too short for a quiet repository, and the
  fallback to a unit's own released archive widens.

## How I will know it was realised

1. A push that changes only a plugin file starts no Rust build.
2. A plugin release fetches its binaries from the last `rust-tool` run and
   completes in minutes.
3. The core npm tarball carries six platform binaries; the other five
   carry none.
4. With the core package installed, a wrapper in any other package runs
   its subcommand through the core binary; without it, the wrapper reports
   unrun.

## Consequences

- A push that changes only plugin files starts no Rust build; the three
  workflows each own one stage.
- The release workflows read the last successful Rust Tool run's
  artifacts, so a quiet repository's plugin release depends on that run
  surviving retention.
- The five non-core Pi packages ship without binaries and without an
  installer; their tarballs shrink to their own files.
- The core package's extension is the one place that puts the meow binary
  on PATH, and every other package's launcher degrades through it.
- The Claude Code marketplace keeps its per-unit feature binaries, built
  by the same Rust Tool workflow.

## What this does not settle

- The Claude Code units' switch to the shared binary.
- Artifact retention beyond the platform default.
- Whether the meow-full release version and the installers' pinned version
  converge on one source.
