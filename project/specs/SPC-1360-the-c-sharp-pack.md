---
id: SPC-1360
artifact: spec
status: live
revised: 2026-10-13
states: [REQ-2340, REQ-2422, REQ-2428, REQ-2442, REQ-2444, REQ-2448, REQ-3048]
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The C# pack

## Scope

This covers `meow-csharp`, the language pack for C# on .NET. It states what
`status` detects, what `bind` prints and what `check` finds. Every rule
SPC-1190 states for a language pack holds here, and this document states only
what is C#'s. It leaves the supply-chain audit, a preview opt-in and the
solution format's migration to the skill, because no command reports them.

ADR-2660 decides this pack.

## Boundary

| Surface                                                | What it is                                                      |
| ------------------------------------------------------ | --------------------------------------------------------------- |
| `plugins/meow-csharp/bin/meow-csharp`                  | The program: `status`, `bind` and `check`                       |
| `plugins/meow-csharp/skills/csharp/SKILL.md`           | The skill                                                       |
| `plugins/meow-csharp/skills/csharp/reviewing.md`       | What a reviewer of C# needs beyond the commands                 |
| `plugins/meow-csharp/README.md`                        | The unit's page, with the toolchain versions it's current as of |
| `global.json`, `Directory.Build.props`, each `.csproj` | What the pack reads to bind and to check                        |

The program is the `csharp` feature of `crates/meow`. It runs git alone, and
reads the SDKs installed under the `dotnet` root from the directory listing,
starting no .NET tool (SPC-1190).

## Behaviour

### Detection

A directory activates the pack where git tracks a `*.sln`, `*.slnx`,
`*.slnf` or `*.csproj` file in it (REQ-2340, RES-0105). A directory holding a
project and lying under a directory that holds a solution is covered by that
solution and doesn't activate on its own (REQ-3048). Each report names the
directory and the marker files it found there.

A directory's target is its one `*.slnx` or `*.sln`, then its one `*.slnf`,
then its one `*.csproj`. A directory holding two candidates at the first level
that has any binds no stage, and each stage names both files, because the pack
never picks between two solutions.

### The pinned SDK

Where `global.json` sets `sdk.version` in the directory or an ancestor up to
the root, `status` prints the pin, its `rollForward` and the SDKs installed
under the `dotnet` root: `$DOTNET_ROOT`, or the directory holding the
`dotnet` that `PATH` finds, with links resolved (REQ-2428, RES-0360). The pin
is met where an installed SDK satisfies the `rollForward` policy, `patch`
where none is set. An unmet pin prints `unresolved: dotnet <pin> pinned,
<installed> installed`, and `status` and `bind` exit 3. Every bound command
runs through `dotnet`, which applies the pin itself.

### What `bind` prints

Every bound command restores explicitly and passes `--no-restore` after it,
because each later command otherwise restores again (REQ-2448). Every bound
command passes one `--artifacts-path` outside the working tree,
`${TMPDIR:-/tmp}/meow-csharp/<repository>/<directory>`, so `bin` and `obj`
never land beside a project (REQ-2442, RES-0360). `<restore>` below stands for
`dotnet restore <target> --artifacts-path <out> &&`.

| Stage    | Printed as                                                                       | When                                                                                           |
| -------- | -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `format` | `dotnet csharpier check .`                                                       | A `.csharpierrc*` or `csharpier.yaml`, or `csharpier` in `.config/dotnet-tools.json`           |
| `format` | `# format: unbound, ...`                                                         | Otherwise, naming that `dotnet format` restores into `obj/` beside each project                |
| `lint`   | `<restore> dotnet build <target> --no-restore --artifacts-path <out>`            | `TreatWarningsAsErrors` is `true` in `Directory.Build.props` or a project                      |
| `lint`   | `# lint: unbound, ...`                                                           | Otherwise, because the compiler then fails on no analyser finding (REQ-2422)                   |
| `check`  | `<restore> dotnet build <target> --no-restore --artifacts-path <out>`            | Always                                                                                         |
| `test`   | `<restore> dotnet test <target> --no-restore --artifacts-path <out> <trx>`       | A project references `Microsoft.NET.Test.Sdk`, xunit, NUnit or MSTest, or sets `IsTestProject` |
| `build`  | `<restore> dotnet build <target> --no-restore -c Release --artifacts-path <out>` | Always                                                                                         |

`<trx>` is `--logger trx --results-directory <out>/test` under VSTest. Where
`global.json` sets `test.runner` to `Microsoft.Testing.Platform`, `test` names
its target with `--solution` or `--project` and ends with
`--results-directory <out>/test -- --report-trx`, and a comment says that mode
takes `--artifacts-path` from .NET 11 and `--report-trx` needs
`Microsoft.Testing.Extensions.TrxReport` (RES-0105, RES-0360). The pack turns on
no warning as an error, no analysis level and no nullable context the
repository didn't set (REQ-2422). Under `lint` and `check`, a comment names
the `AnalysisLevel` the compiler runs at, or that the SDK's default applies
where none is set (REQ-2444). `build` uses the `Release` configuration, a
choice this pack makes because `dotnet publish` defaults to it.

### What `check` finds

`check` reads `Directory.Build.props` in the directory and its ancestors and
every project under the directory, and prints a finding for each of these
settings that no file sets (REQ-2444, RES-0105):

| Finding                                                     | When                                       |
| ----------------------------------------------------------- | ------------------------------------------ |
| `<dir>: Nullable isn't enabled`                             | No file sets `<Nullable>enable</Nullable>` |
| `<dir>: TreatWarningsAsErrors isn't set`                    | No file sets it to `true`                  |
| `<dir>: AnalysisLevel isn't set, the SDK's default applies` | No file sets `<AnalysisLevel>`             |

`check` exits 1 on any finding, and prints `no findings` and exits 0 when there
is none.

## Failure paths

| State                                               | Reported as                                              | Exit |
| --------------------------------------------------- | -------------------------------------------------------- | ---- |
| No marker is tracked                                | `unresolved: not a C# repository`                        | 3    |
| The pinned SDK isn't installed                      | `unresolved: dotnet <pin> pinned, <installed> installed` | 3    |
| `check` finds no profile, or one that doesn't parse | `unresolved: <what is wrong with the file>`              | 3    |
| An unknown argument                                 | the usage line                                           | 2    |

`bind` prints its table where the pin isn't met, with a comment naming the
state, because `dotnet` applies the pin itself and the commands stand once the
SDK is installed.

## Questions

Answer each question from what this document states, or leave `unanswered`,
because a gap left visible is one a reader can act on, and a gap left out
reads as covered.

### What the part is for

Detects C# on .NET, binds its stages and checks its configuration.

### What it depends on

`meow-csharp` lists `meow-core` in its `requires.toml`.

### What depends on it

No unit lists `meow-csharp` in its `requires.toml`.

### Where its data lives

It holds none of its own: it reads the files git tracks and the profile, and SPC-1190 states that a pack's program writes no file.

### What crosses a trust boundary

unanswered

### How it fails

Stated under "Failure paths" in this document.

### How it is deployed

`meow-csharp` installs as a plugin from the marketplace, `plugins/meow-csharp/`, and ships as the Pi package `packages/meow-csharp/`.
