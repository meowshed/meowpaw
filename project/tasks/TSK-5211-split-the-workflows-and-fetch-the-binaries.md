---
id: TSK-5211
artifact: task
status: done
revised: 2026-10-04
epic: EPC-2730
closes: [REQ-4142]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Split the workflows and fetch the binaries from the Rust Tool run

`rust-tool.yml` is the one workflow that compiles Rust, started by a
`crates/**` change, by hand or by a `meow-full-v<version>` tag.
`claude-release.yml` and `pi-release.yml` fetch the `bin-<target>` and
`full-<target>` artifacts from the latest successful Rust Tool run on the
trunk and never build.

## Acceptance criteria

1. Given a push that changes only a plugin file, when the workflows
   evaluate, then no Rust build starts. Closed by: the paths filter on the
   Rust Tool trigger, and the release workflows declaring no build job.
2. Given a successful Rust Tool run on the trunk, when a release workflow
   runs, then it fetches the artifacts of that run by its id. Closed by:
   the `run-id` download in both release workflows and a live run.
3. Given no successful Rust Tool run on the trunk, when a release workflow
   runs, then it fails naming the Rust Tool workflow. Closed by: the
   guard's error message.

## What to do

Split build.yml into `rust-tool.yml` with the three family jobs and the
meow-full release; rewrite the two release workflows to resolve the last
successful `rust-tool` run on main and download its artifacts with
`run-id`.

## Depends on

Nothing.

## Evidence

Run 37206994135 of `rust-tool.yml` on main completed with all six build
jobs succeeding and no macOS or Windows runner; the crates-push path
filter and the three workflow files are on the trunk. `pi-release` on
37207568449 fetched the `full-*` artifacts by that run's id, placed them
into the core package and published, proving the fetch chain. The guard
that fails a release without a successful Rust Tool run fired in the
cancelled run 37206982184, which stopped at the artifact-fetch guard.

## Left alone

The build jobs' internals, which the split carries unchanged; the
per-unit feature builds for the Claude Code marketplace, which REQ-0076
keeps; the meow-full release version, which stays the installer's pinned
value.
