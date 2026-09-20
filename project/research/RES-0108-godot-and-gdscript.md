---
id: RES-0108
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0006, RES-0005
---

# Godot and GDScript

## Summary

The engine supplies three verbs and an independent package supplies the other
two, which is where the path problem comes from. One finding costs the most
time when missed. A release export imports nothing where a debug export
imports, so a clean checkout exports assets nobody imported and fails in a way
that reads as a project defect. Identifier files are project state, and
ignoring them breaks every collaborator's scene links while working for the
author.

Research for one supported language and the engine it belongs to. A toolchain
is a set of tools, and this one is split down the middle. The engine supplies
the compiler, the runner and the exporter, and an independent Python package
supplies the formatter and the linter.

It covers what marks a Godot project, how the verbs work when the compiler is a
game engine, and what has to happen before an export. It also covers what
belongs in version control, what the pack authors, and what the skill has to
contain.

It does not cover what every toolchain document shares, which is
[RES-0006-toolchains.md](RES-0006-toolchains.md).

## The question

GDScript is the only language here whose toolchain is maintained outside its
vendor, and the only one where the project's source includes binary-adjacent
state that the engine regenerates. Both facts change what a pack may do rather
than only what it runs.

## Method

We fetched and read the engine's own documentation on 2026-09-20. The
command-line reference, read line by line for which flags imply which, is how
the import asymmetry turned up. The version-control page is where the
credentials warning for older engines came from.

We read the release cadence from the download archive and estimated nothing,
and the identifier-file behaviour was taken from the engine's own announcement
plus one secondary account of the failure mode.

Nothing was installed or run; no export was performed to reproduce the import
asymmetry, which is stated from the documentation.

## Findings

### The markers are the project file and the things the engine generates around it

`project.godot` marks the project and records the engine features it was
created against. Beside it:

- `export_presets.cfg` - the export targets, and in Godot 3.x and 4.0 a file
  that _"may store sensitive credentials"_, which 4.1 and later do not.
- `*.import` files beside every imported asset.
- `*.uid` files beside scripts and resources, introduced in 4.4.
- `.godot/` - the cache directory, including `uid_cache.bin`.
- `addons/` - installed plugins, which may or may not be vendored.
- `*.tscn`, `*.tres`, `*.gd`, `*.gdshader` - the text formats that make a Godot
  project reviewable at all.

The engine's release line moves quickly: 4.7-stable on 18 June 2026, 4.7.1 on
14 July, 4.7.2 on 18 August 2026, with 4.6.3 in May before it. A maintenance
release every four to six weeks means the declared version and the installed
engine diverge by default, and that divergence is what a pack reports rather
than resolves.

### What is committed and what is ignored is a correctness question

The engine's own guidance names `.godot/` as cache data to ignore, alongside
`*.translation`, which is generated from CSV. It also warns that the ignore
list for 3.x and 4.0 is _entirely_ different from later versions, which is why
a copied `.gitignore` from a tutorial is a hazard.

The `.uid` files are the opposite case and the one that goes wrong most. They
are project state, and no build output: ignoring them means every clone
generates fresh identifiers, and every scene referencing a script points at an
identifier that exists only on the original author's machine. The result is
broken scene-to-script links for every collaborator, appearing as a project
that works for one person.

So the rule a pack carries is short and has a reason attached: commit `.uid`
and `.import`, ignore `.godot/`, and check the version before copying any
other advice.

The credentials note is the one that touches the harness's own prohibitions
directly. A repository on an older engine may have secrets in
`export_presets.cfg`, so a tool that packs a repository for reading excludes
it, and relies on nothing being safe.

### The verbs run the engine headless, and three of them are the engine

| Verb        | Command                                                                               |
| ----------- | ------------------------------------------------------------------------------------- |
| `fmt`       | `gdformat`                                                                            |
| `lint`      | `gdlint`                                                                              |
| `typecheck` | `godot --headless --check-only --script <file>`                                       |
| `test`      | GUT or GdUnit4, headless                                                              |
| `build`     | `godot --headless --import`, then `godot --headless --export-release <preset> <path>` |

`--headless` is _"required on platforms without GPU access"_, which is every
continuous integration machine, and also stops a window appearing during an
export on a machine that has one.

`--check-only` _"Only parse for errors and quit (use with `--script`)"_, which
makes the type verb a parse check, and no full analysis. That is an honest
limit to state: it catches syntax and resolution errors, where a typed language
would catch more.

### The export has a prerequisite that one of its own forms hides

This is the finding that costs the most time when it is missed. `--import`
_"Starts the editor, waits for any resources to be imported, and then quits"_.
It is implied by `--export-debug` and `--export-pack`.

It is **not** implied by `--export-release`.

So a release export on a clean checkout - which is every continuous
integration run, since `.godot/` is correctly ignored - runs against assets
that were never imported. A pack that resolves `build` to `--export-release`
alone produces a failure that looks like a project defect, and the fix is a
step nobody wrote down.

The same applies before a headless test run that loads scenes.

### The formatter and linter are a Python package, which is where the path problem comes from

`gdtoolkit` supplies four tools: `gdformat`, `gdlint`, `gdparse` for a parse
tree, and `gdradon` for cyclomatic complexity. It installs with `pip3 install
"gdtoolkit==4.*"` or through `pipx`, with a separate 3.x line for Godot 3.

Because it installs into a Python environment and never beside the engine, the
tools are on the path only when that environment is active. Calling them by
absolute path removes the dependency on shell state - the same finding as `uv
run` in Python, arriving from a different direction.

The package's major version tracks the engine's major version, and never its
minor: the 4.x line covers Godot 4 as a whole. A project on Godot 3 needs the
3.x line, and mixing them produces parse errors that look like syntax errors in
correct code.

`gdradon` deserves a mention it rarely gets. Complexity measurement is the only
tool here that reports on how the code is arranged, where the others report on
its correctness, and it feeds a review and gates nothing.

### The toolchain, tool by tool

| Role             | Tool                            | Comes from                       |
| ---------------- | ------------------------------- | -------------------------------- |
| Compile, parse   | `godot --check-only`            | the engine                       |
| Run, export      | `godot --headless`              | the engine                       |
| Export templates | a separate download per version | the engine                       |
| Format           | `gdformat`                      | gdtoolkit                        |
| Lint             | `gdlint`                        | gdtoolkit                        |
| Parse tree       | `gdparse`                       | gdtoolkit                        |
| Complexity       | `gdradon`                       | gdtoolkit                        |
| Test             | GUT                             | the asset library                |
| Test             | GdUnit4                         | the asset library                |
| Native code      | `godot-cpp`, GDExtension        | the engine, plus a C++ toolchain |

Export templates are the row that surprises a pack author. They are matched to
the engine version and downloaded separately, so a `build` verb fails for a
reason that is neither the project nor the engine binary. Saying which is the
difference between a useful failure and a confusing one.

A project using GDExtension has a second toolchain underneath it - a C++ build
with `scons` or CMake - which is outside this document and has to be detected,
never ignored.

### Test results are citable because the frameworks emit JUnit XML

GUT and GdUnit4 both run headless and both produce JUnit XML. That counts for
more than which one the project chose. Evidence for a task has to be a file
somebody can read later, and a framework that only prints to a terminal
produces a result that exists once.

Both need the project imported first, for the same reason the export does.

### What the pack authors

`project.godot` - which is an INI-shaped file the engine rewrites, so editing
it by hand risks losing ordering the engine expects - and the export presets,
carefully, given what older versions store in them.

A `.gitignore` matched to the engine version, which is one of the few files
where a pack's default is materially better than a copied one.

A continuous integration workflow with the import step, the version pin and the
template download, which is the part every project gets wrong at least once.

### What a reviewer needs that no command reports

Static typing in GDScript, which is optional and changes the generated code as
well as the checking. Untyped code is a finding, and no style choice, and the
linter does not require it.

Node lifetime: `_init` against `_ready`, `queue_free` and the references that
outlive it.

Signals as the decoupling mechanism, and who owns a connection - a connection
nobody disconnects is a reference nobody released.

Scene ownership and `PackedScene` instancing, where the same scene is a
template and an instance and the distinction is invisible in the script.

`@export` and what the inspector can set to a value the code never expects.

The main thread, `call_deferred`, and what may not touch the scene tree from
elsewhere.

Resources as shared mutable state, which is the defect that appears when two
nodes edit what looks like their own copy.

For a `.gdshader`: render modes, what belongs in the vertex stage against the
fragment stage, and uniform naming.

And for the scene files themselves: a `.tscn` is text and therefore reviewable,
which most Godot projects never take advantage of. A change to a scene is a
diff, and reading it is the only way to see a node reparented.

### What the skill has to contain

In the body, in this order:

1. Detection. `project.godot` and the generated files around it, with the
   engine version read from the project file and compared with the installed
   binary.
2. The import rule, before the verbs. `--export-release` does not import;
   `--export-debug` and `--export-pack` do; a headless test run that loads
   scenes needs it too.
3. Verb resolution, with the engine binary and the export templates named
   as environment dependencies that fail distinctly from the project.
4. Version control. Commit `.uid` and `.import`, ignore `.godot/`, and the
   reason for each.
5. What must never happen. Reading `export_presets.cfg` on an older engine,
   which may hold credentials. Mixing gdtoolkit lines. Calling gdtoolkit
   through the path. Reporting an untyped script as clean.

In supporting files: the tool inventory, a version-matched `.gitignore`, and a
continuous integration workflow with import, templates and a version pin. Also
the two test frameworks' invocations with their JUnit output, the reviewer's
knowledge, and the dated facts with what to re-check: the release cadence, the
gdtoolkit lines and the UID introduction in 4.4.

## Conclusions

1. A Godot project is marked by `project.godot`, which also records the engine
   version it was created against. 2. The declared engine version is compared
   with the installed one and the difference is reported, because patch
   releases arrive every few weeks and a project does not follow them
   automatically. 3. `typecheck` is a parse check and is reported as one.
   `--check-only` parses for errors, which is less than a typed language's
   check, and claiming more would overstate it. 4. `build` imports before it
   exports. `--export-release` does not imply `--import`, so a clean checkout
   exports assets that were never imported and fails for a reason that looks
   like a project defect. 5. A headless test run that loads scenes imports
   first, for the same reason. 6. `--headless` is required on any machine
   without GPU access, and no preference is involved. 7. A missing engine or
   export template is reported as an environment failure, distinctly from a
   failure in the project, because the templates are a separate download
   matched to the version. 8. `.uid` and `.import` files are committed and
   `.godot/` is ignored, with the reason stated: ignoring the identifiers
   breaks every collaborator's scene-to-script links while working for the
   author. 9. Version-control advice is matched to the engine version, since
   the ignore list for 3.x and 4.0 differs entirely from later versions. 10.
   `export_presets.cfg` is treated as possibly holding credentials on Godot 3.x
   and 4.0, so a tool that packs or reads the repository excludes it and
   assumes nothing about it being safe. 11. `fmt` and `lint` come from
   `gdtoolkit` and are invoked by absolute path, because the package installs
   into a Python environment and the path otherwise depends on shell state. 12.
   The `gdtoolkit` major line is matched to the engine major version. The 4.x
   line is for Godot 4 and the 3.x line for Godot 3, and the wrong line reports
   parse errors in correct code. 13. Complexity from `gdradon` feeds a review
   and gates nothing, because it reports on how the code is arranged and never
   on its correctness. 14. A test framework is required to emit JUnit XML,
   because evidence has to be a file readable after the run, and both GUT and
   GdUnit4 do. 15. Untyped GDScript is a finding, and no preference, and the
   linter does not produce it, so it belongs in the reviewer's knowledge. 16. A
   project using GDExtension has a second toolchain, which is detected and
   never ignored. 17. Scene and resource files are text and are reviewed as
   diffs, which is how a reparented node becomes visible. 18. The skill body
   carries detection, the import rule, verb resolution with environment
   dependencies named, the version-control rules, and the prohibitions, in that
   order.

## Sources

All read 2026-09-20.

- [Command line
  tutorial](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html)
  - `--headless` as required on platforms without GPU access; `--import`
    starting the editor, waiting for resources to be imported and quitting;
    `--check-only` parsing for errors only, used with `--script`; `--quit` and
    `--quit-after`; `--path` requiring a directory containing `project.godot`;
    and that `--export-debug` and `--export-pack` imply `--import` while
    `--export-release` does not. - [Version control
    systems](https://docs.godotengine.org/en/stable/tutorials/best_practices/version_control_systems.html)
  - `.godot/` as cache data to ignore and `*.translation` as generated from
    CSV; that the ignore list for Godot 3.x and 4.0 is entirely different from
    later versions; and that Godot 3.x and 4.0 may store sensitive credentials in
    `export_presets.cfg` where 4.1 and later do not. - [UID changes coming to
    Godot 4.4](https://godotengine.org/article/uid-changes-coming-to-godot-4-4/)
    and [Godot 4.4 added .uid files
    everywhere](https://dev.to/ziva/godot-44-added-uid-files-everywhere-heres-what-they-actually-do-4e56)
  - the introduction of `.uid` files; that they are project state and no build
    output, and belong in version control; and the failure mode when they are
    ignored, where each clone generates fresh identifiers and scene-to-script
    references break for every collaborator. - [Godot download
    archive](https://godotengine.org/download/archive/) - the release line with
    4.7-stable on 18 June 2026, 4.7.1 on 14 July 2026, 4.7.2 on 18 August 2026
    and 4.6.3 on 20 May 2026, showing a maintenance release every four to six
    weeks. -
    [godot-gdscript-toolkit](https://github.com/Scony/godot-gdscript-toolkit) -
    the four tools `gdformat`, `gdlint`, `gdparse` and `gdradon`, the last a
    cyclomatic complexity measure; installation through `pip3 install
"gdtoolkit==4.*"` or `pipx`; and the separate 4.x and 3.x lines for Godot 4
    and Godot 3.
