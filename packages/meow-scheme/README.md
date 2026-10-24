---
reader: someone installing or running meow-scheme on Pi
answers: what meow-scheme provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-scheme@0.1.1]
---

# @meowshed/meow-scheme

Detects Scheme projects from the manifests git tracks, names the implementation before it binds anything, prints a stages table that binds Racket's tests as raco test without writing bytecode and binds nothing for an implementation whose commands the repository doesn't commit, reports a stage that writes bytecode into the working tree and a compiled directory that isn't ignored, writing no file, and carries what a reviewer of Scheme checks that no command reports. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-scheme
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

## Bind your stages

`meow-scheme bind` prints a `[stages]` table for you to paste into
`.meowpaw/profile.toml`, and never writes the profile itself:

| Stage    | Bound to                    | When                                                      |
| -------- | --------------------------- | --------------------------------------------------------- |
| `format` | nothing, printed as unbound | Racket: `raco fmt` has no check mode                      |
| `lint`   | nothing, printed as unbound | Always: no linter is committed                            |
| `check`  | nothing, printed as unbound | Racket: `raco make` writes `compiled/` beside each source |
| `test`   | `raco test --table .`       | Racket                                                    |
| `build`  | nothing, printed as unbound | Racket: for the reason `check` gives                      |

The pack binds `raco test` without `--make` and binds no `raco make`, because
only those write bytecode into your working tree, and it runs the test in the
directory holding `info.rkt`, where `raco test` finds your tests. Racket has no
machine-readable report, so the evidence is captured output with the table
`--table` prints: exit 0 means every test passed, 2 a timeout and 1 another
failure. CHICKEN and Guile bind nothing, because a Scheme test library runs
nothing and no command is committed. A stage you already declared is left out
of the table.

## Check your repository

`meow-scheme check` prints a finding for each of these and exits 1 on any:

| Line                                                           | When                                                     |
| -------------------------------------------------------------- | -------------------------------------------------------- |
| `<stage> runs raco make or --make, which writes compiled/ ...` | A stage runs `raco make`, `--make` or `-y`               |
| `<dir>: compiled/ isn't ignored`                               | A Racket directory and no ignore rule covers `compiled/` |
| `<dir>: compiled/ is tracked: <file>`                          | Git tracks a file under `compiled/`                      |

With no finding it prints `no findings` and the groups it checked, and exits 0.

## What it reports instead of a table

| Line                                                   | Means                                                  |
| ------------------------------------------------------ | ------------------------------------------------------ |
| `unresolved: not a Scheme repository`                  | Git tracks no manifest                                 |
| `unresolved: Racket and CHICKEN are all detected, ...` | A directory holds the manifests of two implementations |
| `unresolved: no profile at .meowpaw/profile.toml`      | `check` found no profile                               |
| `unresolved: the profile doesn't parse: ...`           | The profile isn't valid TOML                           |

Each exits 3.

## Generated files

Commit `info.rkt`: it is project state, and it declares which paths `raco
test` skips and includes. Ignore `compiled/`, the bytecode `raco make` and
`raco test --make` write beside each source. `status` states both for each
Racket directory, and `check` reports a `compiled/` nothing ignores or git
tracks.

## Review Scheme

When Pi reviews Scheme, the skill has it run `status` first and then
load `reviewing.md`, which holds what no command reports: tail position,
hygienic macros and what `syntax-rules` can't express, continuations against
`dynamic-wind`, mutation as the exception, and the SRFIs a file assumes. The
skill never runs a command from one implementation against another's project,
never reports a zero exit status from an unidentified implementation as a
pass, and never claims coverage outside Racket.

## What it costs you

The skill's description stays in context on every turn, and `reviewing.md`
costs context only when Scheme is reviewed. The program is a native binary
shipped inside `meow-core`, and needs git on the machine. On a machine the
unit carries no binary for, it reports the repository as unresolved and exits 3.

## Read a subcommand's help

`meow-scheme --help` lists the subcommands, and `meow-scheme <subcommand> --help`
names what it determines, what you read to reach the same answer without the
tool, and the first word of each kind of line it prints.
