---
id: SPC-1080
artifact: spec
status: live
revised: 2026-09-26
checked-at:
states: [REQ-0032, REQ-0074, REQ-0076, REQ-3178]
---

# The native tool

## Scope

This covers `meow`, the one command-line tool every unit's program is a
subcommand of: where its source lives, how a unit gets a binary built with its
own features, how a unit's launcher finds and runs it, and how a release ships
it. What each subcommand does is its unit's specification: SPC-1040 for the
verbs, SPC-1050 for the commit check, SPC-1060 for the `git` pack and SPC-1070
for the record checks.

The harness doesn't implement this yet. ADR-1110 decides it and EPC-1080
realises it, so `checked-at` stays empty until that epic closes.

## Boundary

| Surface                         | What it is                                                              |
| ------------------------------- | ----------------------------------------------------------------------- |
| `crates/meow/`                  | The tool's source: one crate, with a feature per unit and its own tests |
| `plugins/<unit>/bin/<unit>`     | The unit's launcher, which picks the binary for the machine             |
| `plugins/<unit>/bin/<target>/`  | The unit's binaries, one per target, built and never committed          |
| `.github/workflows/release.yml` | The release: six targets, one archive per unit, a marketplace file      |

## Behaviour

### One crate, a feature per unit

The crate `crates/meow/` builds one binary, `meow`, whose subcommands are the
units' programs: `verbs`, `scm`, `git` and `record`. Each subcommand sits behind
a feature named for its unit, and a unit's binary is built with that unit's
feature alone, so it carries its own code and nothing of another unit's
(REQ-0076). The profile reading, the report shapes and the exit codes the
units share are one module every feature uses.

### The launcher

`plugins/<unit>/bin/<unit>` stays the command a skill or hook runs. It names the
machine's target from the operating system and the processor, looks for
`bin/<target>/meow`, sets its executable bit if the delivery didn't keep it,
and runs it with the unit's subcommand and the arguments it was given. Where no
binary exists for the target, it reports every check as unrun and exits as the
unit's specification says a missing program does, never with success on a
check.

### Six targets

| Target                       | Serves                                 |
| ---------------------------- | -------------------------------------- |
| `aarch64-apple-darwin`       | macOS on Apple silicon                 |
| `x86_64-apple-darwin`        | macOS on Intel                         |
| `aarch64-unknown-linux-musl` | Linux on ARM64, glibc and Alpine alike |
| `x86_64-unknown-linux-musl`  | Linux on x64, glibc and Alpine alike   |
| `aarch64-pc-windows-msvc`    | Windows on ARM64                       |
| `x86_64-pc-windows-msvc`     | Windows on x64                         |

### Building locally

`mise run build` builds each unit's binary for the machine it runs on into the
unit's `bin/<target>/`, which `.gitignore` excludes, so a checkout loaded in
place by a local-directory marketplace runs the tool without a release. The
gate runs the crate's tests, and this repository's `test` verb runs the units'
fixtures against the launchers.

### A release

A person runs the release workflow by hand, and it builds all six targets with
`crates/meow/build-units <target>`, the script the local build runs. It packs
each unit whose version has no release yet as a zip of the unit's tracked files
and its binaries, and publishes it as a release tagged `<unit>-v<version>`, so
each unit carries its own version (REQ-0074). A unit whose version already has
a release keeps its archive. A release named `marketplace` holds one
`marketplace.json` whose entries point at every unit's archive by `url` and
`sha256`. Claude Code reads an address on `github.com` as a git repository, so
a person downloads the file and adds it by its path (RES-0274):

```bash
curl -fsSLo marketplace.json https://github.com/meowshed/meowpaw/releases/download/marketplace/marketplace.json
claude plugin marketplace add ./marketplace.json
```

A later release reaches that person when they download the file again.

A person installs a released unit from that marketplace and never needs Rust,
Python or Node.js. The repository's own `marketplace.json` keeps its relative
paths for development. Run without publishing, the workflow builds and packs
only, and leaves the archives, their sizes and their SHA-256 as a workflow
artifact.

### What stays optional

The features of the tool that read the record and project it onto a tracker,
which later decisions add, are features no step of the method depends on
(REQ-0032). A unit is complete with the record kept by hand and no tracker.

## Failure paths

| Condition                              | What happens                                            |
| -------------------------------------- | ------------------------------------------------------- |
| No binary for the machine's target     | The launcher reports every check as unrun, never passed |
| The binary has lost its executable bit | The launcher sets it and runs the binary                |
| A unit's feature fails to build        | The gate fails, naming the unit                         |
| A target fails to build at release     | The release publishes nothing, and names the target     |
