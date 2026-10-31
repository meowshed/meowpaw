---
id: TSK-5210
artifact: task
status: done
revised: 2026-10-04
epic: EPC-2720
closes: [REQ-4142]
issue: 852
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Build every target under Linux

The build workflow runs no macOS and no Windows runner: the musl targets
build natively, the windows targets through cargo-xwin, and the darwin
targets through osxcross in a container, with `ldid` signing every darwin
binary before it is packed and the installer signing again after download.
The Claude Code marketplace release keeps its per-unit archives carrying
all six platforms, built by the same jobs.

## Acceptance criteria

1. Given the build workflow, when a run completes, then the `bin-<target>`
   artifacts exist for all six targets and no job ran on a macOS or
   Windows runner. Closed by: the workflow run's job list and artifacts.
2. Given a darwin binary from that run, when `codesign -dv` reads it on a
   Mac, then it shows an ad-hoc signature. Closed by: installing the
   binary from the run's archive and reading the signature.
3. Given a Pi session with a Linux-built meow binary installed, when a
   guard command runs, then the binary executes. Closed by: a session
   dispatching the loop guard.
4. Given the marketplace release workflow, when it packs a unit whose
   version has no release, then the archive carries `bin/<triple>/meow`
   for all six platforms. Closed by: the release step's next run, whose
   notes table lists six platforms per unit.

## What to do

The `linux`, `darwin` and `windows` jobs in `build.yml` each build the
per-unit binaries and the all-features binary for their targets; the
darwin job signs with `ldid` and pins the osxcross image; `build-units`
calls `cargo xwin build` for a windows target and plain `cargo build`
otherwise; the installer's codesign step covers a binary placed by hand.

## Depends on

Nothing.

## Evidence

Run 37203557611: the six build jobs named `linux`, `darwin` and `windows`
all succeeded, and no job ran on a macOS or Windows runner; the full
artifacts fed `meow-full-v0.1.0.zip`, which `file` reads as Mach-O arm64,
Mach-O x86_64, PE32+ Windows arm64 and x64, and ELF musl arm64 and x64.
`codesign -dv` on the Linux-built `meow-aarch64-apple-darwin` shows its
ad-hoc signature, and the binary runs on this machine printing all thirteen
subcommands. The `bin-<target>` artifacts keep the `plugins/*/bin/<target>`
layout the marketplace release packs, so its archives carry six platforms
when it next runs.

## Left alone

The release.yml pack step and the wrappers, which the artifacts' shape
keeps byte-compatible; the requires.toml files, which name no runner; the
existing released archives, which stay as released.
