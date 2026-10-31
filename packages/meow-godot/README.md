---
reader: someone installing or running meow-godot on Pi
answers: what meow-godot provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-godot@0.2.0]
---

# @meowshed/meow-godot

Detects Godot projects from what git tracks, reads the engine version from each project file before it binds anything, prints a stages table bound from the gdtoolkit, GUT and export preset files the repository committed with an import before every export and its output outside the working tree, reports an engine cache or identifier file ignored or committed wrongly, writing no file, and carries what a reviewer of GDScript and scenes checks that no command reports. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-godot
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

`meow-godot bind` prints a `[stages]` table for you to paste into
`.meowpaw/profile.toml`, and never writes the profile itself:

| Stage    | Bound to                                                   | When                                                          |
| -------- | ---------------------------------------------------------- | ------------------------------------------------------------- |
| `format` | `gdformat --check .`                                       | A `gdformatrc` in the directory                               |
| `lint`   | `gdlint .`                                                 | A `gdlintrc` or `.gdlintrc` in the directory                  |
| `check`  | nothing, printed as unbound                                | Always: `--check-only` parses the one script `--script` names |
| `test`   | `godot --headless --path <dir> -s addons/gut/gut_cmdln.gd` | A `.gutconfig.json` and the GUT script, on Godot 4            |
| `build`  | `godot --headless --path <dir> --export-release <preset>`  | A preset with an `export_path`, on Godot 4.1 or later         |

`test` and `build` run `godot --headless --path <dir> --import` first, because
`--export-release` imports nothing and a headless test run that loads scenes
needs the import a clean checkout never made. `test` writes GUT's JUnit XML to
`junit.xml`, and `build` exports the first preset that names an
`export_path`, both under `$XDG_STATE_HOME/meowpaw/packs/meow-godot/`, outside
your working tree, and a comment names each other preset. On an engine older
than 4.1 `build` stays unbound and the pack doesn't read `export_presets.cfg`,
because those versions may store credentials in it. gdtoolkit and GUT bind only
where you committed their files. A stage you already declared is left out of
the table.

## Check your repository

`meow-godot check` prints a finding for each of these and exits 1 on any:

| Line                                                                        | When                                                              |
| --------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `<dir>: .godot/ isn't ignored`                                              | No ignore rule covers the engine's cache                          |
| `<dir>: .godot/ is tracked: <file>`                                         | Git tracks a file under the cache                                 |
| `<dir>: *.import files are ignored`                                         | An ignore rule covers the import files                            |
| `<dir>: *.uid files are ignored`                                            | On Godot 4.4 or later, an ignore rule covers the identifier files |
| `<dir>: export_presets.cfg is tracked, and Godot ... may store credentials` | The engine is older than 4.1                                      |
| `<stage> exports with --export-release and imports nothing first`           | A stage in your profile skips the import                          |

With no finding it prints `no findings` and the groups it checked, and exits 0.

## What it reports instead of a table

| Line                                                 | Means                                  |
| ---------------------------------------------------- | -------------------------------------- |
| `unresolved: not a Godot and GDScript repository`    | Git tracks no `project.godot`          |
| `unresolved: Godot engine version not detected: ...` | A project file names no engine version |
| `unresolved: no profile at .meowpaw/profile.toml`    | `check` found no profile               |
| `unresolved: the profile doesn't parse: ...`         | The profile isn't valid TOML           |

Each exits 3.

## Generated files

Commit `*.import` files and, from Godot 4.4, `*.uid` files: they are project
state, and ignoring the identifiers gives every clone fresh ones, so scene
links to scripts break for everyone but the author. Ignore `.godot/`, the
engine's cache. The ignore list for Godot 3 and 4.0 differs entirely from
later versions, so check the engine version before you copy a `.gitignore`.
`status` states both lists for each project, and `check` reports a file on the
wrong side.

## Review Godot and GDScript

When Pi reviews GDScript, the skill has it run `status` first and then
load `reviewing.md`, which holds what no command reports: static typing, node
lifetime, signals and who owns a connection, scene ownership and instancing,
what `@export` lets the inspector set, the main thread, resources as shared
state, shaders, and scene files as text to read as a diff. The skill never
calls gdtoolkit through whatever is on the path, never reads
`export_presets.cfg` on an engine older than 4.1, and never reports an untyped
script as clean.

## What it costs you

The skill's description stays in context on every turn, and `reviewing.md`
costs context only when Godot and GDScript is reviewed. The program is a native binary
shipped inside `meow-core`, and needs git on the machine. On a machine the
unit carries no binary for, it reports the repository as unresolved and exits 3.

## Read a subcommand's help

`meow-godot --help` lists the subcommands, and `meow-godot <subcommand> --help`
names what it determines, what you read to reach the same answer without the
tool, and the first word of each kind of line it prints.
