---
reader: someone choosing or running meow-scheme
answers: what meow-scheme does, what it adds to a session and how to run it
kind: reference
describes: [meow-scheme@0.1.0]
---

# meow-scheme

`meow-scheme` tells you where your repository holds a Scheme project and which
implementation runs it, prints a `[stages]` table that binds Racket's tests
and nothing a Scheme implementation could run in the wrong place, and checks
that your stages write no bytecode into your working tree. Its skill tells
Claude Code what a reviewer of Scheme checks that no command reports. It
writes no file and starts no Scheme implementation: `status`, `bind` and
`check` read the files git tracks and run git alone. It installs on its own,
with no other part of the `meowpaw` harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://paw.retran.me/meowpaw/marketplace.json
claude plugin install meow-scheme@meowpaw
```

Installing this unit also enables `meow-core`, which ships the shared `paw` binary its launcher runs, and the platform keeps `meow-core` enabled while this unit is on, so you can't disable `meow-core` alone.

Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions, because the unit's behaviour was never seen on an older one.

## Run it

Claude Code puts the unit's `bin/` directory on its Bash tool's `PATH`, so
Claude Code runs it in your repository as:

```bash
meow-scheme status
```

From your own shell, run the same launcher by its path in the installed unit.

The program reports for each directory where git tracks an `info.rkt`, which
marks Racket, a `.egg` file, which marks CHICKEN, or a `guix.scm`, which marks
a Guix package and so Guile. A `.scm` file alone activates nothing, because it
names Scheme and no implementation.

The implementation comes first, because a command from the wrong one often
succeeds and does something else, so a zero exit status from an unidentified
implementation is no evidence. A directory holding the manifests of two
implementations prints `unresolved: Racket and CHICKEN are all detected` and
exits 3, and `bind` prints every stage of that directory unresolved with that
reason. For Racket, `status` also prints which test paths `info.rkt` declares,
or that it declares none and `raco test` runs every file under the directory.

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

When Claude Code reviews Scheme, the skill has it run `status` first and then
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

## What it needs

Claude Code 2.1.280 or later, declared in `plugins/meow-scheme/requires.toml`, and git.
The pack is current as of Racket's documentation for `raco test`, `raco make` and `raco fmt` as read on 2026-10-13 and CHICKEN 5's extensions chapter, none observed running. Check a binding against a newer
tool's documentation before you trust it.
