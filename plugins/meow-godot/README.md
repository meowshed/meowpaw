---
reader: someone choosing or running meow-godot
answers: what meow-godot does, what it adds to a session and how to run it
kind: reference
describes: [meow-godot@0.1.0]
---

# meow-godot

`meow-godot` tells you where your repository holds a Godot project and which
engine version its project file names, prints a `[stages]` table bound from
the gdtoolkit, GUT and export preset files you committed, and checks that the
engine's cache is ignored and its identifier files are committed. Its skill
tells Claude Code what a reviewer of GDScript and scenes checks that no
command reports. It writes no file and starts no Godot tool: `status`, `bind`
and `check` read the files git tracks and run git alone. It installs on its
own, with no other part of the `meowpaw` harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://paw.retran.me/meowpaw/marketplace.json
claude plugin install meow-godot@meowpaw
```

Installing this unit also enables `meow-core`, which ships the shared `paw` binary its launcher runs, and the platform keeps `meow-core` enabled while this unit is on, so you can't disable `meow-core` alone.

Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions, because the unit's behaviour was never seen on an older one.

## Run it

Claude Code puts the unit's `bin/` directory on its Bash tool's `PATH`, so
Claude Code runs it in your repository as:

```bash
meow-godot status
```

From your own shell, run the same launcher by its path in the installed unit.

The program reports for each directory where git tracks a `project.godot`.
For each directory, `status` prints the engine version, the tools your
repository configured and the generated files to commit and to ignore.

The engine version comes first, read from the first entry of
`config/features` in `project.godot`, such as `4.3` in
`PackedStringArray("4.3", "Forward Plus")`. `config_version` names the file's
format and is never read as the engine's version. Where the file names none,
`status` prints `unresolved: Godot engine version not detected` and exits 3,
and `bind` prints every stage of that directory unresolved with that reason,
because a command line written for Godot 3 fails on a Godot 4 project in a way
that looks like the project's defect.

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

When Claude Code reviews GDScript, the skill has it run `status` first and then
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

## What it needs

Claude Code 2.1.280 or later, declared in `plugins/meow-godot/requires.toml`, and git.
The pack is current as of Godot 4.7 and gdtoolkit 4.x as the research read them in September 2026, GUT's command line and Godot's command-line reference as read on 2026-10-13. Check a binding against a newer
tool's documentation before you trust it.
