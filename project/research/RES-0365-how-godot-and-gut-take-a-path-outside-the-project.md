---
id: RES-0365
artifact: research
status: approved
revised: 2026-10-13
elaborates: RES-0108, RES-0360
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Godot exports to an absolute path whose directory exists, and GUT runs with the project named by its path

## Summary

Godot's command line takes an absolute export path, so a Godot pack can put
the exported binary outside the working tree, provided it makes the target
directory first and names the file, because the engine requires both. The
`--script` option resolves a relative path against the project, and GUT's own
examples run it with `--path` naming the project, so one command runs a
project in a subdirectory without changing directory. GUT exits 0 when every
test passes and 1 when any fails. GUT's page doesn't say whether
`-gjunit_xml_file` takes an absolute path, so a pack that passes one relies on
the engine's file access, which this record didn't confirm.

## The question

SPC-1190 has a Godot pack keep each stage's output outside the working tree
and collect test results as JUnit XML. RES-0108 and RES-0360 name the flags
but not what path forms they take or what a run's exit status means, so a
binding written from them would guess whether an absolute path works.

## Method

I read Godot's command-line tutorial and GUT's command-line page on
2026-10-13. Nothing was run, because no Godot engine is installed on this
machine.

## Findings

### An export takes an absolute path, and its directory must exist

The tutorial says of `--export-release` that _"`<path>` should be absolute or
relative to the project directory, and include the filename for the binary"_,
and that _"The target directory must exist."_ A relative path is _"relative to
the directory containing the `project.godot` file"_. Export templates _"must
be installed for the editor (or a valid custom export template must be
defined in the export preset)"_.

### `--script` resolves against the project, and `--path` names the project

`--script` takes _"a resource path relative to the project (`myscript.gd`
will be interpreted as `res://my_script.gd`) or an absolute filesystem
path"_, and `--path` takes a directory that _"must contain a "project.godot"
file"_. GUT's page runs `godot -d -s --path "$PWD" addons/gut/gut_cmdln.gd`
and `godot -s addons/gut/gut_cmdln.gd -d --path "$PWD" ... -gexit`.

### GUT's exit status says whether every test passed

GUT's page says _"`0` will be returned if all tests pass and `1` will be
returned if any fail (`pending` doesn't affect the return value)"_, and
`-gjunit_xml_file` _"Export results of run to this file in the Junit XML
format"_. The page says nothing about the forms of path that option takes.

## Conclusions

1. A Godot pack exports to an absolute path outside the working tree, makes
   that directory before the export, and names the file the preset names,
   because the engine requires the directory to exist and the filename to be
   given.
2. A Godot pack runs a project in a subdirectory with `--path <directory>`
   and GUT's script as `-s addons/gut/gut_cmdln.gd`, because the script path
   resolves against the project.
3. A Godot pack reads a test run's result from GUT's exit status and its
   JUnit XML file, and states that an absolute path for that file is
   unconfirmed.

## Sources

- [Godot command line tutorial](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html),
  read 2026-10-13 - `--export-release` paths, the existing directory, export
  templates, `--script` and `--path`.
- [GUT command line](https://gut.readthedocs.io/en/latest/Command-Line.html),
  read 2026-10-13 - the example command lines, the exit status and
  `-gjunit_xml_file`.
