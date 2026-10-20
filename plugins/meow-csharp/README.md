---
reader: someone choosing or running meow-csharp
answers: what meow-csharp does, what it adds to a session and how to run it
kind: reference
describes: [meow-csharp@0.1.0]
---

# meow-csharp

`meow-csharp` tells you where your repository holds a .NET solution or
project, which SDK it pins and whether that SDK is installed, prints a
`[stages]` table bound from what you committed, and checks the three settings
that decide whether your lint means anything. Its skill tells Claude Code what
a reviewer of C# checks that no command reports. It writes no file and starts
no .NET tool: `status`, `bind` and `check` read the files git tracks and run
git alone. It installs on its own, with no other part of the `meowpaw`
harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://paw.retran.me/meowpaw/marketplace.json
claude plugin install meow-csharp@meowpaw
```

Installing this unit also enables `meow-core`, which ships the shared `paw` binary its launcher runs, and the platform keeps `meow-core` enabled while this unit is on, so you can't disable `meow-core` alone.

Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions, because the unit's behaviour was never seen on an older one.

## Run it

Claude Code puts the unit's `bin/` directory on its Bash tool's `PATH`, so
Claude Code runs it in your repository as:

```bash
meow-csharp status
```

From your own shell, run the same launcher by its path in the installed unit.

The program reports for each directory where git tracks a `*.sln`, `*.slnx`,
`*.slnf` or `*.csproj` file, and names the files it found there. A project
inside a directory holding a solution belongs to that solution and isn't
reported again. Each directory's report opens with `scope: <directory>` and
one `marker: <file>` line for each file, and then `status` prints:

1. The SDK `global.json` pins, its `rollForward` policy and the SDKs installed
   under `$DOTNET_ROOT`, or under the directory of the `dotnet` on your
   `PATH`.
2. The test runner `global.json` selects, VSTest where it selects none.
3. The formatter you configured: CSharpier, or none.
4. The `AnalysisLevel` your projects set, or that the SDK's default applies.
5. The target the stages build: the directory's one solution, then its one
   solution filter, then its one project.

Every command that reads the profile first prints its state, `profile: absent`,
`profile: unparseable` or `profile: parsed`, and `unknown key: <path>` for each
key no unit reads.

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

When Claude Code reviews C#, the skill has it run `status` first and then load
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

## What it needs

Claude Code 2.1.280 or later, declared in `plugins/meow-csharp/requires.toml`,
and git. The pack is current as of the .NET 10 SDK and CSharpier's `check`
command, read from their documentation on 2026-10-13 and not yet observed running, so check a
binding against a newer SDK's documentation before you trust it.
