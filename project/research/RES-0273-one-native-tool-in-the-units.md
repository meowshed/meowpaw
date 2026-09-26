---
id: RES-0273
artifact: research
status: approved
revised: 2026-09-26
elaborates: RES-0025, RES-0264
---

# One native tool, shipped inside the units

## Summary

A single native binary, built for each platform Claude Code supports and
shipped inside the units, can carry every unit's program and the tool that
reads the record. The platform copies a plugin's files into its cache or loads
them in place, lets a marketplace pin a plugin to an archive by its SHA-256,
and supports six operating system and processor pairs. A binary delivered this
way keeps its executable bit through `git` and isn't quarantined on macOS. The
alternative the harness uses today, an interpreter already on the machine,
isn't guaranteed: Claude Code ships as a native binary that invokes no
Node.js, and nothing installs Python.

Carrying the tool inside the units reverses RES-0025's eighth conclusion,
that the tool is separate and required by nothing. What survives from it is
REQ-0032's rule that adoption is complete at each level: the tool's features
that read the record and project it onto a tracker stay optional, and no step
of the method depends on them.

## The question

ADR-1070 gave each unit a program written for an interpreter the harness
doesn't install, and three units now depend on it. The owner asked for one
native tool in Rust instead, extended as the harness grows, and for the tool
the requirements already describe to be the same one. Can a plugin ship a
native binary to every machine Claude Code runs on, without a separate install,
and what does combining the tools cost against what the record already
decided?

## Method

The guide to Claude Code's documentation read its pages on loading plugins,
the marketplace reference and the setup page on 2026-09-26, and quoted each
answer with its source. I checked two things on this machine, macOS 27.0 on
Apple silicon with Rust 1.98.1: what a binary delivered by `git clone`
carries, and how large a small Rust binary is. The second failed, because the
linker needs the Xcode licence accepted and that needs the owner. I read
RES-0025 and the approved requirements that describe the tool.

## Findings

### Where a plugin's files end up

"Every other marketplace plugin: Claude Code copies the plugin into
`cache/<marketplace>/<plugin>/<version>/` at install and loads that copy."
A plugin with a relative path in a marketplace added from a local directory
"loads in place from its path inside the marketplace folder", as this
repository's plugins do. Nothing documented limits a plugin's size, apart from
256 MiB for a command source in copy mode.

### A marketplace can pin a plugin to an archive or a commit

A plugin's source can be a relative path, `github`, `url`, `git-subdir`, `npm`,
`archive` or `command`. The three `git` forms take a `ref`, "a branch or tag",
and a `sha`, "a full 40-character lowercase commit SHA". An `archive` source
takes a `url` and a `sha256`. A release can therefore publish the units with
their binaries as an archive pinned by its hash, and the binaries never enter
the repository's history.

### The executable bit and macOS quarantine

The documentation says nothing about file permissions or a `bin/` directory.
On this machine, a binary committed to a repository and cloned kept its mode,
`-rwxr-xr-x`, and carried only the `com.apple.provenance` attribute and not
`com.apple.quarantine`, so Gatekeeper doesn't stop it. Whether an archive keeps
the bit depends on the archive format, so a launcher that sets the bit on
first run doesn't depend on it.

### The platforms

Claude Code runs on macOS 13.0 and later, Windows 10 1809 and later or Windows
Server 2019 and later, Ubuntu 20.04 and later, Debian 10 and later, and Alpine
Linux 3.19 and later, on "x64 or ARM64" processors. That is six targets: macOS,
Linux and Windows, each on x64 and ARM64. A Linux binary linked statically
against musl runs on both the glibc distributions and Alpine, so Linux needs
one build per processor.

### No interpreter is guaranteed

"The npm package installs the same native binary as the standalone installer
... The installed `claude` binary does not itself invoke Node." A machine
running Claude Code may have neither Node.js nor Python. The three units built
under ADR-1070 report every check as unrun where Python 3.11 is missing, which
is honest and, on such a machine, useless.

### The size of the binary

Not measured. A release build of a small program with a TOML parser, JSON
output and regular expressions failed to link: "You have not agreed to the
Xcode license agreements." The owner accepting the licence unblocks the
measurement.

### What the record already says about a tool

RES-0025 researched `meow-book`, "a local-first project management system over
the same Markdown corpus", and concluded that "the tool is separate, optional,
and required by nothing". The requirements carry the parts of that that bind:
adoption is complete "at three levels: the kernel alone, the method with the
record kept by hand, and the method with the tool that reads the record"
(REQ-0032); the method completes with no tracker (REQ-1380); and the record
can be projected onto a tracker "with no tool, by ordinary commands"
(REQ-1402). None of them requires the tool to ship separately. They require
that the method not depend on its record and tracker features.

## Conclusions

1. A plugin can carry a native binary to every machine Claude Code runs on,
   built for six targets, with no separate install.
2. A release publishes the units and their binaries as an archive pinned by
   its SHA-256, so the binaries stay out of the repository's history.
3. A launcher sets the binary's executable bit where the delivery didn't keep
   it, because the documentation doesn't promise it.
4. A native binary removes the interpreter dependency, which matters because
   no interpreter is guaranteed on a machine running Claude Code.
5. One tool can carry every unit's program and the features that read the
   record, provided the method never depends on the second kind, which is what
   REQ-0032, REQ-1380 and REQ-1402 require. RES-0025's conclusion that the
   tool ships separately doesn't survive this, and the decision that combines
   them has to say so.
6. The binary's size is unmeasured, and the decision states it as a cost to
   measure before the first release.

## Sources

- [Plugin loading](https://code.claude.com/docs/en/plugins/loading.md), read
  2026-09-26 - the cache path, loading in place for a local directory, and the
  sources that are copied.
- [Plugin marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference.md),
  read 2026-09-26 - the seven source forms, `ref`, `sha` and `sha256`, and the
  256 MiB limit for a command source in copy mode.
- [Set up Claude Code](https://code.claude.com/docs/en/setup.md), read
  2026-09-26 - the supported systems and processors, and the native binary
  that invokes no Node.js.
- A `git clone` of a repository holding a binary, on macOS 27.0, 2026-09-26 -
  the executable bit kept, and `com.apple.provenance` without
  `com.apple.quarantine`.
- A `cargo build --release` on Rust 1.98.1, 2026-09-26 - the failure to link
  without the Xcode licence.
- [RES-0025-management-system.md](RES-0025-management-system.md) - the tool as
  separate and optional, and the conclusion this record reverses.
