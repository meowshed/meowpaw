---
id: SPC-1380
artifact: spec
status: live
revised: 2026-10-13
states:
  [
    REQ-2346,
    REQ-2416,
    REQ-2420,
    REQ-2442,
    REQ-2446,
    REQ-2448,
    REQ-2450,
    REQ-3048,
  ]
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The Godot and GDScript pack

## Scope

This covers `meow-godot`, the language pack for Godot projects and the
GDScript in them. It states what `status` detects, what `bind` prints and what
`check` finds. Every rule SPC-1190 states for a language pack holds here, and
this document states only what is Godot's. It leaves GdUnit4, `gdradon`, a
GDExtension's native build and the comparison of the project's engine version
with the installed engine unbound, because `status`, `bind` and `check` start
no tool and the installed version is only known by running the engine.

ADR-2660 decides this pack and EPC-2560's TSK-5105 ships it.

## Boundary

| Surface                                        | What it is                                                      |
| ---------------------------------------------- | --------------------------------------------------------------- |
| `plugins/meow-godot/bin/meow-godot`            | The program: `status`, `bind` and `check`                       |
| `plugins/meow-godot/skills/godot/SKILL.md`     | The skill                                                       |
| `plugins/meow-godot/skills/godot/reviewing.md` | What a reviewer of GDScript and scenes needs beyond the program |
| `plugins/meow-godot/README.md`                 | The unit's page, with the toolchain versions it's current as of |

The program is the `godot` feature of `crates/meow`. It runs git alone, as
`git ls-files` and `git check-ignore`, and starts no Godot tool (SPC-1190).
The pack reads no table of its own in the profile, because the project file
names everything it needs.

## Behaviour

### Detection

A directory activates the pack where git tracks a `project.godot` in it
(REQ-2346, RES-0108). Each report opens with the directory's scope line and
names the marker (REQ-3048).

### The engine version

The pack reads the engine version from the first entry of
`config/features` under `[application]` in `project.godot`, such as `4.3` in
`config/features=PackedStringArray("4.3", "Forward Plus")`, before it binds
any stage (REQ-2446, RES-0360). `config_version` names the project file's
format and is never read as the engine's version. A directory whose project
file names no version prints `unresolved: Godot engine version not detected:
<file> names none in config/features` in `status`, and `bind` prints each of
its stages unresolved with that reason, because a Godot 3 command line run
against a Godot 4 project, or the reverse, fails for a reason that looks like
the project's.

### What `bind` prints

Each command runs in the directory the marker activates, with the engine
given `--path <directory>` and gdtoolkit run from that directory:

| Stage    | Printed as                                                                         | When                                                                                     |
| -------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `format` | `gdformat --check .`                                                               | A `gdformatrc` in the directory                                                          |
| `lint`   | `gdlint .`                                                                         | A `gdlintrc` or `.gdlintrc` in the directory                                             |
| `check`  | `# check: unbound, ...`                                                            | Always, because `--check-only` parses one script given with `--script`                   |
| `test`   | the import, then `godot --headless --path <dir> -s addons/gut/gut_cmdln.gd -gexit` | A `.gutconfig.json` and a tracked `addons/gut/gut_cmdln.gd` in the directory, on Godot 4 |
| `build`  | the import, then `godot --headless --path <dir> --export-release "<preset>" <out>` | A preset with an `export_path` in `export_presets.cfg`, on Godot 4.1 or later            |
| any      | `# <stage>: unbound, looked for <files>`                                           | No row above applies                                                                     |

The pack binds gdtoolkit only where its configuration file is committed, and
GUT only where `.gutconfig.json` is, because neither ships with the engine
and the repository chooses each (REQ-2420, RES-0360). gdtoolkit's
documentation doesn't say where it searches for its files, so the pack reads
them in the directory it binds for (RES-0360). A `.gutconfig.json` without a
tracked `addons/gut/gut_cmdln.gd` leaves `test` unbound naming the missing
script, because the run needs it.

`test` and `build` run `godot --headless --path <dir> --import` first,
because `--export-release` imports nothing and a headless test run loads
scenes a clean checkout never imported (REQ-2448, RES-0108). `test` asks GUT
for JUnit XML with `-gjunit_xml_file=<out>/junit.xml`, and `build` exports
the first preset to `<out>/<file>`, where `<file>` is the last component of
the preset's `export_path` (REQ-2416, RES-0365). `<out>` is
`${XDG_STATE_HOME:-$HOME/.local/state}/meowpaw/packs/meow-godot/<directory>`,
with the root written as `root`, made with `mkdir -p` before the run, because the engine needs the directory
to exist and the tree has to stay as it was (REQ-2442, RES-0365). A second
preset is named in a comment under `build`. On an engine older than 4.1,
`build` stays unbound naming the credentials an older `export_presets.cfg`
may hold, and the pack doesn't read that file (RES-0108). On an engine older
than 4, `test` and `build` stay unresolved, because the pack binds Godot 4's
command line alone.

The engine writes its cache, `.godot/`, in the project's directory, and no
documented flag moves it, so the pack keeps it ignored through `check`
in place of moving it (REQ-2442, RES-0108).

Where several directories activate, a stage joins each directory's bound
command with `&&`, and a directory that leaves the stage unbound or
unresolved is a comment naming the directory. `bind` prints nothing for a
stage the profile declares, exits 3 where any directory's engine version
isn't detected, and exits 0 otherwise.

### Generated files

`status` prints, for each directory, `commit: *.import and *.uid, which are
project state` and `ignore: .godot/, which is the engine's cache`, the
`*.uid` part from Godot 4.4 on, because ignoring identifier files breaks every
collaborator's scene links while working for the author (REQ-2450, RES-0108).

### What `check` finds

| Finding                                                                           | When                                                               |
| --------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| `<dir>: .godot/ isn't ignored`                                                    | `git check-ignore` finds no rule ignoring the engine's cache       |
| `<dir>: .godot/ is tracked: <file>`                                               | Git tracks a file under the cache                                  |
| `<dir>: *.import files are ignored`                                               | An ignore rule covers the import files, which are project state    |
| `<dir>: *.uid files are ignored`                                                  | On Godot 4.4 or later, an ignore rule covers the identifier files  |
| `<dir>: export_presets.cfg is tracked, and Godot <version> may store credentials` | The engine is older than 4.1 and git tracks its presets            |
| `<stage> exports with --export-release and imports nothing first`                 | A stage's command runs `--export-release` with no `--import` in it |

`check` exits 1 on any finding, and prints `no findings` with what it checked
and exits 0 when there is none (REQ-2450, REQ-2448).

## Failure paths

| State                                  | Reported as                                          | Exit |
| -------------------------------------- | ---------------------------------------------------- | ---- |
| No `project.godot` is tracked          | `unresolved: not a Godot and GDScript repository`    | 3    |
| A project file names no engine version | `unresolved: Godot engine version not detected: ...` | 3    |
| The profile doesn't parse              | `unresolved: the profile doesn't parse: ...`         | 3    |
| `check` finds no profile               | `unresolved: no profile at .meowpaw/profile.toml`    | 3    |
| An unknown argument                    | the usage line                                       | 2    |
