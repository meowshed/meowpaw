---
reader: someone installing or running meow-checks on Pi
answers: what meow-checks provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-checks@0.14.0]
---

# @meowshed/meow-checks

Runs a repository's five verification stages, format, lint, check, test and build, from the commands it declares in .meowpaw/profile.toml, and reports a stage with no command as unresolved, never as passed. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-checks
```

The paw executable ships with `@meowshed/meow-core` alone (REQ-4612): this
package's launchers run their subcommands through it, so install the core
package beside this one for the binary-backed checks. Without it, every
check reports unrun and lets the command through.

```bash
pi install npm:@meowshed/meow-core   # carries the binary the launchers run
```

Installing from this repository's checkout is the development install: it
loads the package in place and runs no lifecycle script.

## Declare your stages

Put one command per stage in `.meowpaw/profile.toml` at the repository's root.
Each command runs through the shell from that root:

```toml
[stages]
format = "./scripts/format --check"
lint = "./scripts/lint"
test = "./scripts/run-tests"
```

Declare only the stages your repository has. A stage you leave out is reported
as unresolved, which is the honest answer: nothing ran, so nothing passed.

### Declare the parts of a repository

If your repository is built from parts that are checked differently, such as
a crate and a site, name each part and its directory under `[parts]` in the
root profile:

```toml
[parts]
site = "site"
engine = "crates/engine"
```

Give a part its own stages in `.meowpaw/profile.toml` inside its directory.
The program reads that file over the root's: a key the part declares replaces
the root's for that part, and a stage the part leaves out is unresolved there,
because the root's command was written for the root and never for the part.
A part with no profile of its own takes the root's. A part's profile can't
move the record or declare parts, so `[record]` or `[parts]` in it is named as
`unknown key: record (in site/.meowpaw/profile.toml)` and the root's stands.
A repository that declares no `[parts]` is one part, its root.

`status`, `run` and `evidence` take `--part <name>`. With no `--part`, they
work on the part whose directory holds your current directory, and on the
root where none does. A part's stages run from the part's directory:

```fish
meow-checks run test --part site
```

Every report names what it covered on a line of its own, `scope: site site`
for a part, its name and its directory, or `scope: repository`. `evidence`
for a part reads only that part's runs, because a pass at the root says
nothing about the part. Each ledger record keeps its scope and the directory
the run started in. A `--part` that names no declared part exits 2, names the
parts the profile declares and runs nothing.

## Find out whether you can work here

`meow-checks doctor` answers one question: can this repository be worked on on
this machine. Where the work stands is `paw status`'s question, and neither
command answers the other's.

```fish
meow-checks doctor
```

It prints the profile's state, then each stage's resolution for the
repository and for each part, then one line for each pack installed beside
this unit, naming the marker file it matched and its directory:

```text
pack: meow-markdown matched .markdownlint-cli2.yaml in .
pack: meow-mise matched mise.toml in .
```

A pack you haven't installed can't report its marker, so it isn't named. Each
finding follows on a `finding:` line, marked `machine` where it depends on
this machine, such as a stage whose program isn't on your `PATH`, and
`repository` where the repository has to change, such as an unresolved stage.
`doctor` exits 0 with no finding, 1 where a finding concerns the repository,
and 3 where every finding is marked `machine`. It runs no stage, repairs
nothing and writes nothing, the ledger included.

## What it costs you The

program is a native binary shipped inside the unit, so it needs nothing
installed on the machine. On a machine the unit carries no binary for, every
stage is reported unresolved, as "no interpreter".

## Read a subcommand's help

`meow-checks --help` lists the subcommands, and `meow-checks <subcommand> --help` names
what it determines, what you read to reach the same answer without the tool,
and the first word of each kind of line it prints. A test holds each
subcommand's output to those words.
