---
reader: someone choosing or running meow-starlark
answers: what meow-starlark does, what it adds to a session and how to run it
kind: reference
describes: [meow-starlark@0.2.1]
description: "Detects Bazel and Buck workspaces from what git tracks, names the build system that evaluates the Starlark before it binds anything, prints a stages table bound from the buildifier configuration and the workspace file the repository committed with Bazel's symlinks switched off, reports a stage that passes whatever buildifier finds, rewrites files or leaves output in the working tree, writing no file, and carries what a reviewer of Starlark checks that no command reports."
---

# meow-starlark

`meow-starlark` tells you where your repository holds a Bazel or Buck
workspace and which build system evaluates its Starlark, prints a `[stages]`
table bound from the buildifier configuration and workspace file you
committed, and checks that your stages neither pass whatever buildifier finds
nor write into your working tree. Its skill tells Claude Code what a reviewer
of Starlark checks that no command reports. It writes no file and starts no
Bazel, Buck or buildifier process: `status`, `bind` and `check` read the files
git tracks and run git alone. It installs on its own, with no other part of
the `meowpaw` harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-starlark@meowpaw
```

Installing this unit also enables `meow-core`, which ships the shared `paw` binary its launcher runs, and the platform keeps `meow-core` enabled while this unit is on, so you can't disable `meow-core` alone.

Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions, because the unit's behaviour was never seen on an older one.

## Run it

<!-- host-specific: claude -->

Claude Code puts the unit's `bin/` directory on its Bash tool's `PATH`, so
Claude Code runs it in your repository as:

```bash
meow-starlark status
```

From your own shell, run the same launcher by its path in the installed unit.

The program reports for each directory where git tracks a `MODULE.bazel`,
`REPO.bazel`, `WORKSPACE` or `WORKSPACE.bazel`, which marks a Bazel workspace,
or a `.buckconfig`, which marks a Buck project. For each directory, `status`
prints the build system and the buildifier configuration.

The build system comes first, because the implementations differ in the
functions they provide, and a file that formats cleanly may call one its
evaluator lacks. A directory holding both a Bazel and a Buck marker prints
`unresolved: Bazel and Buck are all detected` and exits 3, and `bind` prints
every stage of that directory unresolved with that reason.

## Bind your stages

`meow-starlark bind` prints a `[stages]` table for you to paste into
`.meowpaw/profile.toml`, and never writes the profile itself:

| Stage    | Bound to                                   | When                                            |
| -------- | ------------------------------------------ | ----------------------------------------------- |
| `format` | `buildifier --mode=check -r .`             | A `.buildifier.json` in the directory           |
| `lint`   | `buildifier --mode=check --lint=warn -r .` | A `.buildifier.json` whose `lint` key is `warn` |
| `check`  | nothing, printed as unresolved             | Always: Starlark has no static types            |
| `test`   | `bazel test --symlink_prefix=/ ... //...`  | A Bazel workspace                               |
| `build`  | `bazel build --symlink_prefix=/ //...`     | A Bazel workspace                               |

Every buildifier command passes `--mode=check`, because the default mode
rewrites the files it checks, and none passes `--format`, because buildifier
exits 0 whenever it is given one, so the stage would pass whatever it found.
The evidence of those stages is captured output: exit 4 means a file needs
reformatting or a lint warning was found. Every Bazel command passes
`--symlink_prefix=/`, because the convenience symlinks are the only output
Bazel writes into your workspace, and `test` writes the build event protocol
as JSON to `bep.json` under `$XDG_STATE_HOME/meowpaw/packs/meow-starlark/`. A
workspace with no test target makes `bazel test` exit 4. A Buck project binds
no `test` or `build`, because Buck2 writes `buck-out` at the project's root and
documents no flag that moves it. The pack binds neither `buildozer` nor a
linter you didn't configure. A stage you already declared is left out of the
table.

## Check your repository

`meow-starlark check` prints a finding for each of these and exits 1 on any:

| Line                                                               | When                                                    |
| ------------------------------------------------------------------ | ------------------------------------------------------- |
| `<stage> runs buildifier with --format; its exit status is 0 ...`  | A stage runs buildifier with `--format`                 |
| `<stage> runs buildifier without --mode=check, which rewrites ...` | A stage runs buildifier without `--mode=check`          |
| `<stage> runs bazel without --symlink_prefix=/`                    | A stage runs `bazel build` or `bazel test` without it   |
| `<dir>: bazel-* symlinks aren't ignored`                           | Such a stage exists and no ignore rule covers the links |
| `<dir>: buck-out/ isn't ignored`                                   | A Buck project and no ignore rule covers `buck-out`     |

With no finding it prints `no findings` and the groups it checked, and exits 0.

## What it reports instead of a table

| Line                                                  | Means                                  |
| ----------------------------------------------------- | -------------------------------------- |
| `unresolved: not a Starlark repository`               | Git tracks no Bazel or Buck marker     |
| `unresolved: Bazel and Buck are all detected, so ...` | A directory holds both kinds of marker |
| `unresolved: no profile at .meowpaw/profile.toml`     | `check` found no profile               |
| `unresolved: the profile doesn't parse: ...`          | The profile isn't valid TOML           |

Each exits 3.

## Generated files

Commit the workspace markers, `MODULE.bazel` and the others, and
`.buildifier.json`: they are project state. Ignore `bazel-*`, the convenience
symlinks Bazel creates in the workspace unless `--symlink_prefix=/` stops
them, and `buck-out/`, where Buck writes its output. `status` states both
lists, and `check` reports a `buck-out` nothing ignores.

## Review Starlark

When Claude Code reviews Starlark, the skill has it run `status` first and then
load `reviewing.md`, which holds what no command reports: the language's
guarantees as a checklist, the evaluating build system and the functions it
provides, `load()` resolution, and whether a macro should have been a rule.
The skill never treats every `.star` file as Bazel's, never rewrites a `BUILD`
file as text where `buildozer` could change it, and never claims a type
check.

## What it costs you

The skill's description stays in context on every turn, and `reviewing.md`
costs context only when Starlark is reviewed. The program is a native binary
shipped inside `meow-core`, and needs git on the machine. On a machine the
unit carries no binary for, it reports the repository as unresolved and exits 3.

## Read a subcommand's help

`meow-starlark --help` lists the subcommands, and `meow-starlark <subcommand> --help`
names what it determines, what you read to reach the same answer without the
tool, and the first word of each kind of line it prints.

## What it needs

<!-- host-specific: claude -->

Claude Code 2.1.280 or later, declared in `plugins/meow-starlark/requires.toml`, and git.
The pack is current as of buildifier's README and source on its main branch and Bazel's documentation as read on 2026-10-13, none observed running. Check a binding against a newer
tool's documentation before you trust it.
