---
id: ADR-1110
artifact: adr
status: approved
revised: 2026-09-26
addresses: [REQ-0032, REQ-0074, REQ-0076, REQ-3178]
supersedes: []
---

# 1110. One native tool carries every unit's program

## Decision

Every program a unit carries is a subcommand of one command-line tool, `meow`,
written in Rust. `meow verbs`, `meow scm`, `meow git` and `meow record` replace
the programs ADR-1070, ADR-1080 and ADR-1090 wrote for an interpreter, and the
record checks ADR-1100 decides are built in it from the start. The tool is the
one the requirements name as the third level of adoption, "the tool that reads
the record" (REQ-0032), and it grows the features that read the record and
project it onto a tracker in later decisions.

The source is one crate with a feature for each unit. Each unit ships a binary
built with its own features only, so a unit carries what it uses, versions
independently of the others (REQ-0074), and requires none of them (REQ-0076).
A unit that uses another's subcommand where it is installed, as `meow-git`
uses the commit check, keeps doing so through that unit's binary, as REQ-0079
allows.

A unit carries its binary for six targets, macOS, Linux and Windows on x64 and
on ARM64, the platforms Claude Code supports, with Linux linked statically so
one build serves the glibc distributions and Alpine. Nothing is installed
separately (REQ-3178). A release builds the binaries and publishes each unit as
an archive pinned by its SHA-256, so no binary enters the repository's history.
A local checkout builds them with `cargo` into a directory the repository
ignores.

Each unit keeps a launcher at `bin/<unit>` that picks the binary for the
machine, sets its executable bit where the delivery didn't keep it, and runs
it. Where no binary exists for the machine, the launcher reports every check as
unrun, as the interpreter launchers report a missing interpreter today.

The features that read the record and project it onto a tracker stay
optional: no step of the method depends on them, and the method completes with
the record kept by hand and with no tracker (REQ-0032, REQ-1380, REQ-1402).

This amends ADR-1070, whose program was written for an interpreter already on
the machine. What each program does stays as its decision states it, and the
fixtures written for them are the definition the port has to meet.

## Why

The owner asked for one native tool in Rust, extended as the harness grows,
and for the tool the requirements describe to be that same tool. RES-0273
found that no interpreter is guaranteed on a machine running Claude Code,
because the `claude` binary invokes no Node.js and nothing installs Python, so
the three units built on Python report every check as unrun on such a machine.
A native binary shipped inside the unit runs wherever Claude Code does.

One tool and not one per unit, because the units share the profile, the
reporting and the interpreter problem, and a fourth unit written from scratch
would copy all three.

RES-0025 concluded that the tool ships separately and is required by nothing.
This decision reverses the first half: the tool ships inside the units. The
second half survives where the requirements carry it: the method depends on
none of the tool's record and tracker features.

## Alternatives

| Option                                                   | Better at                                       | Why it lost                                                                                          |
| -------------------------------------------------------- | ----------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| One Rust tool, a binary per unit built with its features | Running anywhere Claude Code runs, one codebase | Chosen                                                                                               |
| Keep Python, as ADR-1070 decided                         | Costing nothing now                             | Nothing installs Python, so the units report every check unrun on a machine without it               |
| JavaScript run by Node.js                                | A language many contributors read               | The `claude` binary invokes no Node.js, so Node.js isn't guaranteed either                           |
| One binary with every feature, shipped in every unit     | One build per target, not one per unit          | Every unit carries every other unit's code, six times over                                           |
| The tool installed separately, as RES-0025 planned       | Keeping the units small                         | REQ-3178 forbids requiring a separate install, and the units' checks would stop working without it   |
| The plugin downloads the binary on first use             | Keeping the published archive small             | It installs software at run time, over the network, which REQ-3178 and the threat model pull against |

## What it costs

A build for six targets at every release, and a release that publishes
archives. Continuous integration builds them and runs no model, which the
owner's rule on continuous integration allows.

Each unit's archive carries six binaries. Their size is unmeasured: RES-0273's
build failed on the Xcode licence, and the first build states the number.

The three units built on Python are ported, which is work already done once,
and until the port lands they keep their Python programs.

Contributors need Rust to change a program. Changing a prompt, a skill or the
record needs nothing new.

## What would reverse it

- The binaries' size makes an archive too large to install comfortably, and a
  per-target download becomes worth its cost.
- The platform starts shipping an interpreter it guarantees to a plugin, and a
  unit's program can be a script again.
- A target Claude Code supports can't be built from the crate, and the units
  can't serve it.

## Consequences

- A crate at the repository's root holds the tool, with a feature per unit and
  its own tests, and the gate checks it builds and its tests pass.
- `meow-verbs`, `meow-scm` and `meow-git` are ported, their launchers pick the
  binary, and their Python programs are deleted. Their fixtures run against the
  new launchers unchanged.
- `meow-method`'s record checks, TSK-1330, are built in the crate from the
  start.
- A release workflow builds the six targets and publishes each unit's archive,
  and the marketplace entries for published units point at the archives by
  their SHA-256. How a local checkout and the published marketplace share one
  `marketplace.json` is settled in the specification.

## How I will know it was realised

1. The fixtures of `meow-verbs`, `meow-scm` and `meow-git`, unchanged, pass
   against launchers that run the Rust binary.
2. The crate builds for all six targets in continuous integration.
3. A unit installed from a published archive runs on a machine with neither
   Python nor Node.js.
4. On a machine with no binary for its target, the launcher reports every
   check as unrun, and nothing passes.
5. No binary is in the repository's history, and the Python programs are gone.
6. The size of each unit's archive is published with the release.

## What this does not settle

- The tool's record and tracker features, which later decisions add.
- Signing the binaries, and verifying them on install.
- Windows without the shell Claude Code runs its commands in, which the
  launchers need.
