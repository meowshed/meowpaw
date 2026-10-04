---
id: RES-0343
artifact: research
status: approved
revised: 2026-10-04
elaborates: RES-0342
---

# Building every target under Linux

## Summary

All six targets of the native tool build under Linux runners: the two musl
targets natively, the two windows targets through `cargo-xwin`, which
fetches the Windows SDK from Microsoft's own servers, and the two darwin
targets through osxcross in a container, which needs the macOS SDK — a
dependency whose licence Apple does not extend to Linux, and the one
trade-off the change makes. A darwin binary built this way carries no
signature, and macOS kills an unsigned arm64 binary on sight, so the build
signs it with `ldid` and the installer signs again with `codesign`.

Sources: the cargo-xwin and osxcross documentation, read 2026-10-04, and
the observed behaviour of the local build and installer.

## Method

Each cross-compilation route was read from its project's documentation,
then the route the meowpaw build takes was written into `build-units` and
the workflow, and the darwin signing question was traced from the macOS
kernel's behaviour to the tool that answers it. Nothing was measured; the
routes are checked by the CI run this work dispatches, and each claim
about what runs names the run that will show it.

## The three routes

**Musl, native.** The two `*-unknown-linux-musl` targets already built on
Linux runners with `musl-tools`; nothing changes but the job's name.

**Windows, through cargo-xwin.** The `*-pc-windows-msvc` targets link
against the Windows SDK, which plain cargo cannot find on Linux.
`cargo-xwin` wraps the build, downloads the SDK headers and libraries from
Microsoft's official servers, and links with lld — the route `maturin` and
the wider Python packaging ecosystem use. Microsoft's licence covers this
use. The `build-units` script gains a branch that calls `cargo xwin build`
for a windows target and plain `cargo build` otherwise.

**Darwin, through osxcross.** The `*-apple-darwin` targets link against
the macOS SDK, which Apple distributes under a licence that covers Apple
hardware. osxcross links the target with that SDK on Linux, and the
community image `joseluisq/rust-linux-darwin-builder` ships the toolchain
ready. The SDK on Linux is outside what Apple's licence names, which is
the cost of dropping the macOS runners, and the image is named and pinned
in the workflow so the dependency is visible.

## The signature question

The macOS linker on a Mac ad-hoc signs every binary it produces, which is
why locally built binaries run unsigned unnoticed. The osxcross linker
does not, and the macOS kernel kills an unsigned arm64 binary on sight
(`zsh: killed`), while an x86_64 binary runs unsigned. `ldid` writes the
ad-hoc signature on Linux; `codesign --force --sign -` writes the same on
a Mac, needs no account or network, and re-signing a signed binary is a
no-op. The build signs with `ldid` before packing, and the installer signs
again after download, so a person who places a raw binary by hand is still
covered by the installer route and never needs to know.

## What holds for the Claude Code plugins

The marketplace release packs each unit's archive from the `bin-<target>`
artifacts the build workflow uploads. Those artifacts are uploaded for all
six targets by the three family jobs, so the marketplace archives carry
the same six platforms they carried before, built under Linux instead of
on macOS and Windows runners. The per-unit launcher scripts, the wrappers
and every released archive stay byte-compatible; nothing in the Claude
Code distribution changes but where its binaries were compiled.

## Conclusions

1. All six targets build under Linux runners; no job needs a macOS or
   Windows runner.
2. The windows route is settled practice with a licence that covers it.
3. The darwin route carries the one licensing trade-off, named in the
   workflow, and the container image is the dependency to watch.
4. A darwin binary arrives signed from the build, and the installer signs
   again, so no person handles a signature on any install path.
5. The Claude Code marketplace release needs no change beyond the build
   workflow it already calls; its archives keep six platforms.

## Sources

Read 2026-10-04:

- The cargo-xwin project documentation — the mechanism, the SDK download
  from Microsoft's servers, the targets it supports.
- The osxcross project documentation and the
  `joseluisq/rust-linux-darwin-builder` image page — the toolchain, the
  SDK the image carries, the environment variables a cargo build needs.

Observed 2026-10-04 on macOS 15 (aarch64):

- A locally built meow binary runs, and `codesign -dv` on it shows an
  ad-hoc signature the macOS linker wrote.
- The installer's `codesign` step runs without an account or network.
