---
id: RES-0360
artifact: research
status: approved
revised: 2026-10-13
elaborates: RES-0105, RES-0106, RES-0107, RES-0108, RES-0109, RES-0110
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# What the later language packs bind, and where their tools put their output

## Summary

Each of the five later languages has a documented way to run its verbs from a
clean checkout without writing into the working tree, and each has a file the
repository commits that says which tool or host applies. A .NET command
restores implicitly unless it's given `--no-restore`, and `--artifacts-path`
moves both `bin` and `obj` out of the project directories. Bazel puts its
output outside the workspace and its convenience symlinks inside it, and
`--symlink_prefix=/` stops the symlinks; Buck2 writes `buck-out` at the
project's root and documents no flag that moves it. Godot's project file names
the engine's major and minor version in `config/features`, gdtoolkit and GUT
read named configuration files, LuaLS names the runtime in `.luarc.json`, and
CHICKEN names an egg by its `.egg` file. This document holds the facts the
five language packs' specifications state beyond RES-0105 to RES-0110, and
nothing those documents already hold.

## The question

The five pack specifications have to bind each verb from what the repository
commits, and hold the shared rules SPC-1190 states: a prerequisite performed
explicitly, output kept outside the tree, a pinned toolchain run and compared,
and a host or implementation detected first. RES-0105 to RES-0110 say which
tools each language uses. They don't say which flags keep those tools out of
the working tree, or which committed file names the host's version, so a
binding written from them alone would guess both.

## Method

I read the vendor documentation and one engine source file on 2026-10-13: the
.NET CLI reference pages for `build`, `restore`, `format` and `test`, the
`global.json` reference and the artifacts output page; CSharpier's CLI page;
the LuaLS settings and configuration pages; gdtoolkit's linter and formatter
wiki pages and README; GUT's command-line page; Godot's
`core/config/project_settings.cpp` and `.h` on the `master` branch; Bazel's
command-line reference, external dependency overview and output directory
page; buildifier's README; Buck2's `.buckconfig` and `buck-out` pages; and
CHICKEN 5's extensions chapter, and Racket's pages for `raco test`, bytecode files and `raco fmt`.

Nothing was run, because no .NET SDK, Godot engine, Bazel, Buck2 or Scheme
implementation is installed on this machine. gdtoolkit's documentation doesn't
say where it searches for its configuration files, so the pack reads them at
the directory it binds for and states that.

## Findings

### A .NET command restores implicitly, and `--no-restore` turns that off

The `dotnet build` reference says restore _"is run implicitly by all commands
that require a restore to occur, such as `dotnet new`, `dotnet build`,
`dotnet run`, `dotnet test`, `dotnet publish`, and `dotnet pack`. To disable
implicit restore, use the `--no-restore` option."_ The `dotnet restore` page
names the reason to restore explicitly: build systems _"need to call `dotnet
restore` explicitly to control when the restore occurs"_. `dotnet format`
takes `--no-restore` as well, and its `--verify-no-changes` _"Terminates with
a non zero exit code if any files would have been formatted."_

### `--artifacts-path` moves `bin` and `obj` outside the project, and has to be cascaded

`dotnet build`, `dotnet restore` and `dotnet test` take `--artifacts-path`,
available since the .NET 8 SDK: _"All build output files from the executed
command will go in subfolders under the specified path, separated by
project."_ The artifacts layout page shows both `bin` and `obj` under that
path. The option _"must be explicitly cascaded in any `dotnet` command that
depends on the output of another `dotnet` command, for example, when using
`dotnet build --no-restore`"_. Without it, `dotnet build` writes to
`./bin/<configuration>/<framework>/` beside each project.

### Under Microsoft.Testing.Platform, `dotnet test` names its target and its report differently

The MTP page gives `--project <PROJECT_PATH>` and `--solution
<SOLUTION_PATH>`, of which _"You can use only one"_, and says `--artifacts-path`
is _"Available for MTP mode starting with .NET 11"_. A TRX report is an
argument for the test application, after a literal `--`, as in `dotnet test
--results-directory TestResults -- --report-trx`, and it _"requires the
`Microsoft.Testing.Extensions.TrxReport` package"_. Under VSTest the target is
the positional argument.

### `global.json` pins the SDK, and the muxer fails where the pin can't be met

`sdk.version` _"Requires the full version number, such as 10.0.100"_. With no
`rollForward`, the muxer uses `patch`, which rolls forward to the latest patch
and otherwise fails. `test.runner` selects `Microsoft.Testing.Platform`, from
the .NET 10 SDK, with VSTest the default. The muxer resolves the pin itself on
every command, so a verb run through `dotnet` runs under the pinned SDK or
fails.

### CSharpier checks with its own command

CSharpier's CLI page gives `dotnet csharpier check [<directoryOrFile>]`, which
_"will return exit code 1 if there are unformatted files"_, and names
`.csharpierrc` and `csharpier.yaml` as configuration files.

### LuaLS reads the runtime from `.luarc.json`

`runtime.version` takes `"Lua 5.1"`, `"Lua 5.2"`, `"Lua 5.3"`, `"Lua 5.4"` or
`"LuaJIT"`, defaulting to `"Lua 5.4"`. In `.luarc.json` the key is written
without the `Lua.` prefix, as `"runtime.version": "Lua 5.3"`. A file that
omits it gets the default silently, so the default is no evidence of which
runtime the repository targets.

### Godot's project file names the engine version it was saved by

`ProjectSettings::_get_supported_features` appends `GODOT_VERSION_BRANCH`, the
major and minor version, to `application/config/features`, and the engine
writes `config_version=5` into every project it saves, where
`CONFIG_VERSION = 5`. A project saved by Godot 4 therefore carries a line such
as `config/features=PackedStringArray("4.3", "Forward Plus")` under
`[application]`.

### gdtoolkit and GUT read named configuration files

`gdlint -d` dumps the default configuration to `gdlintrc`, which the linter
then reads, optionally renamed to `.gdlintrc`. `gdformat --dump-default-config`
writes `gdformatrc`, which _"after next `gdformat` execution it will pick"_,
and the README runs `gdformat --check` in continuous integration. GUT loads
`res://.gutconfig.json` by default, runs from `godot -s
addons/gut/gut_cmdln.gd`, exits with `-gexit`, and with `-gjunit_xml_file`
_"Export results of run to this file in the Junit XML format"_.

### Bazel's output is outside the workspace and its symlinks are inside it

A Bazel repository is marked by a boundary file: _"MODULE.bazel ...,
REPO.bazel ..., or in legacy contexts, WORKSPACE or WORKSPACE.bazel"_. The
output root defaults to `~/.cache/bazel` on Linux and `~/Library/Caches/bazel`
on macOS, and the symlinks `bazel-<workspace-name>`, `bazel-out`,
`bazel-testlogs` and `bazel-bin` _"are put in the workspace directory"_. For
`--symlink_prefix`, _"If `/` is passed, then no symlinks are created"_.
`--build_event_json_file` writes _"a JSON serialisation of the build event
protocol to that file"_. buildifier's `--format=json` _"only works in
combination with `--mode=check`"_, and it reads `.buildifier.json`.

### Buck2 writes `buck-out` at the project's root

_"The root of your project must contain a configuration file named
`.buckconfig`"_, and Buck2 _"stores build artifacts in a directory named
buck-out in the root of your project"_. Neither page documents a flag that
moves it outside the tree.

### CHICKEN names an egg by its `.egg` file, and Racket's test summary is a table

CHICKEN 5's extension chapter says _"Eggs need an egg description file `<egg
name>.egg`"_. `raco test --table` _"Print a summary table after all tests"_,
counting from RackUnit's log, which RES-0110 already records as the nearest
Racket has to a report format.

### `raco make` writes bytecode beside each source, and `raco fmt` checks nothing

Racket's bytecode page says a file _"is compiled to bytecode that is saved as
`compiled/<name>_<ext>.zo` relative to the file"_. `raco fmt` _"displays the
formatted programs to the standard output"_, and its one other mode, `-i`,
_"modify the input files in-place"_; it has no mode that reports a difference
and exits non-zero.

## Conclusions

1. A C# pack restores explicitly and passes `--no-restore` to every later
   command, because each of them otherwise restores again implicitly.
2. A C# pack passes one `--artifacts-path` outside the working tree to the
   restore and to every command after it, because the path has to be
   cascaded and without it `bin` and `obj` land beside each project, and
   under Microsoft.Testing.Platform it names the target with `--solution` or
   `--project` and asks for TRX after `--`.
3. A C# pack reads `sdk.version` from `global.json` and compares it with the
   SDKs installed under the `dotnet` root, because the muxer runs the pin or
   fails, and the pack has to say which before a verb fails for it.
4. A C# pack binds CSharpier's check as `dotnet csharpier check .` and the
   SDK's as `dotnet format --verify-no-changes --no-restore`.
5. A Lua pack takes the runtime from `runtime.version` in `.luarc.json`, in
   either the dotted or the nested form, and treats a file without it as
   naming no runtime, because the default applies in silence.
6. A Godot pack reads the engine version from the first entry of
   `config/features` in `project.godot`, and `config_version` says only the
   project file's format.
7. A Godot pack binds gdtoolkit only where `gdformatrc` or `gdlintrc` is
   committed, and GUT only where `.gutconfig.json` is, with its JUnit XML
   written outside the tree.
8. A Starlark pack detects Bazel from `MODULE.bazel`, `REPO.bazel`,
   `WORKSPACE` or `WORKSPACE.bazel`, and Buck from `.buckconfig`.
9. A Starlark pack passes `--symlink_prefix=/` to every Bazel command it
   binds, and a build event JSON file outside the tree to every `bazel test`,
   because the symlinks are the only output Bazel writes into the workspace.
10. A Starlark pack binds no Buck2 build or test, because `buck-out` lands in
    the tree and no documented flag moves it.
11. A Scheme pack detects CHICKEN from a `.egg` file and Racket from
    `info.rkt`, and binds Racket's tests as `raco test --table .`.
12. A Scheme pack binds no `raco make` and no `raco fmt`, because the first
    writes `compiled/` beside each source and the second has no check mode.

## Sources

- [dotnet build](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-build),
  read 2026-10-13, page dated 2026-05-18 - implicit restore, `--no-restore`,
  `--artifacts-path` and the default output path.
- [dotnet restore](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-restore),
  read 2026-10-13 - explicit restore and its `--artifacts-path`.
- [dotnet format](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-format),
  read 2026-10-13 - `--no-restore` and `--verify-no-changes`.
- [dotnet test](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test)
  and [dotnet test with MTP](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test-mtp),
  read 2026-10-13 - the runner `global.json` selects, and how MTP names its
  target, its artifacts path and its TRX report.
- [global.json overview](https://learn.microsoft.com/en-us/dotnet/core/tools/global-json),
  read 2026-10-13 - `sdk.version`, `rollForward` and the matching rules.
- [Artifacts output layout](https://learn.microsoft.com/en-us/dotnet/core/sdk/artifacts-output),
  read 2026-10-13 - `bin` and `obj` under the artifacts path.
- [CSharpier CLI](https://csharpier.com/docs/CLI), read 2026-10-13 - the
  `check` command and its exit code.
- [LuaLS settings](https://luals.github.io/wiki/settings/) and
  [configuration](https://luals.github.io/wiki/configuration/), read
  2026-10-13 - `runtime.version` and the `.luarc.json` key form.
- [Godot `project_settings.cpp` and `project_settings.h`](https://github.com/godotengine/godot/tree/master/core/config),
  `master` read 2026-10-13 - `config/features` and `CONFIG_VERSION`.
- [gdtoolkit linter](https://github.com/Scony/godot-gdscript-toolkit/wiki/3.-Linter),
  [formatter](https://github.com/Scony/godot-gdscript-toolkit/wiki/4.-Formatter)
  and [README](https://github.com/Scony/godot-gdscript-toolkit), read
  2026-10-13 - `gdlintrc`, `gdformatrc` and `gdformat --check`.
- [GUT command line](https://gut.readthedocs.io/en/latest/Command-Line.html),
  read 2026-10-13 - `.gutconfig.json`, `-gexit` and `-gjunit_xml_file`.
- [Bazel external dependencies overview](https://bazel.build/external/overview),
  [output directory layout](https://bazel.build/remote/output-directories) and
  [command-line reference](https://bazel.build/reference/command-line-reference),
  read 2026-10-13 - boundary files, the output root, the symlinks,
  `--symlink_prefix` and `--build_event_json_file`.
- [buildifier README](https://github.com/bazelbuild/buildtools/blob/main/buildifier/README.md),
  read 2026-10-13 - `--format=json` with `--mode=check`, and
  `.buildifier.json`.
- [Buck2 .buckconfig](https://buck2.build/docs/concepts/buckconfig/) and
  [buck-out](https://buck2.build/docs/concepts/buck_out/), read 2026-10-13 -
  the root marker and where artifacts go.
- [CHICKEN 5 extensions](https://wiki.call-cc.org/man/5/Extensions) and
  [raco test](https://docs.racket-lang.org/raco/test.html), read 2026-10-13 -
  the egg file and `--table`.
- [Racket bytecode files](https://docs.racket-lang.org/raco/Bytecode_Files.html)
  and [raco fmt](https://docs.racket-lang.org/fmt/), read 2026-10-13 - where
  `raco make` writes, and that `raco fmt` prints or rewrites.
