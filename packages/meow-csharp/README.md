---
reader: someone installing or running meow-csharp on Pi
answers: what meow-csharp provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-csharp@0.1.1]
---

# @meowshed/meow-csharp

Detects a .NET solution or project from what git tracks, compares the SDK global.json pins with the ones installed, prints a stages table that restores explicitly and keeps every build's output outside the working tree, reports Nullable, TreatWarningsAsErrors and AnalysisLevel left unset, writing no file, and carries what a reviewer of C# checks that no command reports. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-csharp
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

`meow-csharp bind` prints a `[stages]` table for you to paste into
`.meowpaw/profile.toml`, and never writes the profile itself. For a solution
`Shop.slnx` with CSharpier, `TreatWarningsAsErrors` and a test project
configured, it prints:

```toml
[stages]
format = "dotnet csharpier check ."
lint = 'dotnet restore Shop.slnx --artifacts-path "${TMPDIR:-/tmp}/meow-csharp/shop/root" && dotnet build Shop.slnx --no-restore --artifacts-path "${TMPDIR:-/tmp}/meow-csharp/shop/root"'
check = 'dotnet restore Shop.slnx --artifacts-path "${TMPDIR:-/tmp}/meow-csharp/shop/root" && dotnet build Shop.slnx --no-restore --artifacts-path "${TMPDIR:-/tmp}/meow-csharp/shop/root"'
test = 'dotnet restore Shop.slnx --artifacts-path "${TMPDIR:-/tmp}/meow-csharp/shop/root" && dotnet test Shop.slnx --no-restore --artifacts-path "${TMPDIR:-/tmp}/meow-csharp/shop/root" --logger trx --results-directory "${TMPDIR:-/tmp}/meow-csharp/shop/root/test"'
build = 'dotnet restore Shop.slnx --artifacts-path "${TMPDIR:-/tmp}/meow-csharp/shop/root" && dotnet build Shop.slnx --no-restore -c Release --artifacts-path "${TMPDIR:-/tmp}/meow-csharp/shop/root"'
# lint and check run at AnalysisLevel latest-recommended
```

Every command that builds restores first and passes `--no-restore` after, so
a clean checkout fails on the restore and not halfway through a build. Every
`dotnet` command passes one `--artifacts-path` under your temporary
directory, so `bin` and `obj` never land beside your projects.

| Stage    | Bound to                                                   | When                                                                                           |
| -------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `format` | `dotnet csharpier check .`                                 | A `.csharpierrc*` or `csharpier.yaml`, or `csharpier` in `.config/dotnet-tools.json`           |
| `lint`   | restore, then `dotnet build --no-restore`                  | `TreatWarningsAsErrors` is `true` in `Directory.Build.props` or a project                      |
| `check`  | restore, then `dotnet build --no-restore`                  | Always                                                                                         |
| `test`   | restore, then `dotnet test --no-restore` with a TRX report | A project references `Microsoft.NET.Test.Sdk`, xunit, NUnit or MSTest, or sets `IsTestProject` |
| `build`  | restore, then `dotnet build --no-restore -c Release`       | Always                                                                                         |

A stage with no binding is a comment giving the reason. `format` stays
unbound without CSharpier, because `dotnet format` restores into `obj/`
beside each project and takes no artifacts path. `lint` stays unbound
without `TreatWarningsAsErrors`, because the compiler then fails on no
analyser finding, and the pack turns on no strictness you didn't ask for.
Where `global.json` selects Microsoft.Testing.Platform, `test` names its
target with `--solution` or `--project` and asks for `--report-trx` after
`--`, which needs .NET 11 for the artifacts path and the
`Microsoft.Testing.Extensions.TrxReport` package. A directory holding two
solutions binds no stage that needs a target, and each names both files,
because the pack never picks one. `bind` prints nothing for a stage your
profile already declares.

## Check your settings

`meow-csharp check` reads `Directory.Build.props` in each directory and the
ones above it, and every project under it, and prints a finding for each
setting none of them sets:

| Line                                                        | When                                       |
| ----------------------------------------------------------- | ------------------------------------------ |
| `<dir>: Nullable isn't enabled`                             | No file sets `<Nullable>enable</Nullable>` |
| `<dir>: TreatWarningsAsErrors isn't set`                    | No file sets it to `true`                  |
| `<dir>: AnalysisLevel isn't set, the SDK's default applies` | No file sets `<AnalysisLevel>`             |

It exits 1 on any finding, and prints `no findings` and exits 0 when there is
none.

## What it reports instead of a table

| Line                                                     | Means                                                  |
| -------------------------------------------------------- | ------------------------------------------------------ |
| `unresolved: not a C# repository`                        | Git tracks no solution or project file                 |
| `unresolved: dotnet <pin> pinned, <installed> installed` | No installed SDK meets the pin under its `rollForward` |
| `unresolved: no profile at .meowpaw/profile.toml`        | `check` found no profile                               |
| `unresolved: the profile doesn't parse: ...`             | `check` found a profile that isn't valid TOML          |

Each exits 3. `bind` still prints its table where the pin isn't met, because
`dotnet` applies the pin itself and the commands stand once the SDK is
installed.

## Generated files

Commit your solution and project files, `global.json`,
`Directory.Build.props` and `.config/dotnet-tools.json`, because they're the
project state every binding reads. Ignore `bin/` and `obj/`, which
`dotnet build` and `dotnet restore` write beside each project when no
artifacts path is passed. The stages `bind` prints send that output and the
TRX test results under `${TMPDIR:-/tmp}/meow-csharp/`, outside your working
tree, so a run through them leaves neither directory behind.

## Review C# code

When Pi reviews C#, the skill has it run `status` first and then load
`reviewing.md`, which holds what no command reports: nullable warnings left
as suggestions, `async` and `ConfigureAwait` at a library boundary, the scope
of a `using`, what `==` means on a record, where package versions live, the
test framework's conventions, a preview opt-in, and a solution not yet
migrated to `.slnx`. The skill never runs the formatter you didn't configure,
never turns on a warning as an error, never reports NU1900 or NU1905 as a
vulnerability, and never reports a vulnerable-package list without
`--include-transitive`.

## What it costs you

The skill's description stays in context on every turn, and `reviewing.md`
costs context only when C# is reviewed. The program is a native binary
shipped inside `meow-core`, and needs git on the machine. On a machine the
unit carries no binary for, it reports the repository as unresolved and exits 3.

## Read a subcommand's help

`meow-csharp --help` lists the subcommands, and `meow-csharp <subcommand>
--help` names what it determines, what you read to reach the same answer
without the tool, and the first word of each kind of line it prints.
