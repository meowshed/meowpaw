---
id: RES-0105
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0006, RES-0005
---

# The C# toolchain

## Summary

Three verbs are the same command with different arguments, which makes the
commands trivial and hides that everything deciding whether they mean anything
is configuration spread across four files. The ecosystem's real formatter is
not the one the framework ships, and running the wrong one reformats the whole
repository. Supply-chain auditing runs inside restore, its default changed with
the current release, and two of its warning codes are not vulnerabilities at
all.

Research for one supported language. It covers what marks a .NET project, and
what each verb resolves to when the compiler does three of them. It also covers
which tools the ecosystem uses beyond the SDK, and what the skill for this
language has to contain.

It does not cover what every toolchain document shares, which is
[RES-0006-toolchains.md](RES-0006-toolchains.md), nor what a skill costs, which
is [RES-0005-skill-format.md](RES-0005-skill-format.md).

## The question

C# looks like the easiest language here and is not. Three verbs are the same
command with different arguments, which makes the commands trivial. Everything
that decides whether those commands mean anything is configuration spread
across four files, and the ecosystem's real formatter is not the one the SDK
ships.

So the question is what a pack has to read before it is entitled to report a
pass.

## Method

We fetched and read the vendor documentation on 2026-09-20. The solution
command reference gave the format change and the migration path. The package
auditing page, read in full, gave the audit-mode default, the warning codes,
the dedicated-pipeline pattern and the restore output properties.

The formatter comparison came from a secondary source and is marked as one,
because neither vendor documents the other.

One search was used to establish the release train, and the dates it returned
are recorded as reported, read from no release.

Nothing was installed or run.

## Findings

### Four kinds of marker, and detecting only the solution misses most of them

| Marker                     | What it says                                                       |
| -------------------------- | ------------------------------------------------------------------ |
| `*.slnx`                   | A solution created by .NET 10 or later                             |
| `*.sln`                    | A solution created earlier, or never migrated                      |
| `*.slnf`                   | A solution filter: the subset a large repository actually builds   |
| `*.csproj`                 | A project, which may belong to no solution at all                  |
| `Directory.Build.props`    | Repository-wide build and analysis policy                          |
| `Directory.Packages.props` | Central package management: one place for every version            |
| `global.json`              | The pinned SDK version, and from .NET 10 the test runner           |
| `nuget.config`             | Package sources, and separately the audit sources                  |
| `.editorconfig`            | Per-diagnostic severities, which is where lint policy really lives |

The CLI reference is explicit about the solution format. `dotnet new sln`
creates _"an `.slnx` file in the current folder"_, against _"In .NET 9 and
earlier versions, `dotnet new sln` creates an `.sln` file instead"_. Both stay
readable - every `dotnet sln` subcommand accepts either - and `dotnet sln
<file> migrate` _"Generates an `.slnx` solution file from an `.sln` file"_,
failing rather than overwriting where one exists. Solution filters arrived with
.NET 11, created by `dotnet new slnf`.

The reason the format changed is why it matters here: the XML form diffs, and
the old form is a generated block of identifiers where a two-project change
produces an unreadable hunk. A repository that migrated made its solution
reviewable.

`global.json` is the marker a pack must not skip, because it pins the SDK.
Running the verbs under a different SDK than the repository pinned produces
results about a toolchain nobody uses.

### The formatter question has two answers, and the SDK's is not the one most teams pick

`dotnet format` is the official tool, in the SDK since .NET 6, configurable
through `.editorconfig` across a wide range of style settings. It loads
projects through MSBuild, which is why it fails on project types MSBuild cannot
load.

CSharpier is the other answer: _"an opinionated code formatter for c# and
XML"_. Its printing was ported from Prettier, and it follows Prettier's option
philosophy: _"a few basic options that affect formatting"_, with no plans to
add more. It parses with Roslyn and re-prints, so it does not depend on MSBuild
and works on project shapes `dotnet format` cannot load. It installs as a local
tool with `dotnet tool install csharpier` and runs as `dotnet csharpier format
.`, with a check mode for verification. It is third-party and Microsoft does
not support it.

That is a genuine fork in the ecosystem, and no preference, and it decides the
`fmt` verb by detection:

- A `.csharpierrc` in any of its forms, or a `csharpier` entry in
  `.config/dotnet-tools.json`, means the repository chose CSharpier.
- Otherwise `dotnet format`, because it is present wherever the SDK is.

Running the other one reformats the whole repository, which is the largest
possible false diff and the exact failure the detect-never-prefer rule exists
to prevent.

The second consequence is about authoring. A pack adding formatting to a
repository that has neither is making a choice for the project, so the honest
form is to propose it and write nothing. The opinionated tool removes an
argument and adds a dependency Microsoft does not support, and that trade
belongs to the project.

### Three settings decide whether `lint` exists

`lint` in .NET is the compiler plus analysers. Whether it reports anything
depends on:

- `<Nullable>enable</Nullable>`, which moves a class of null dereference from
  run time to compile time.
- `TreatWarningsAsErrors`, or per-diagnostic severities in `.editorconfig`,
  without which every analyser finding is a message nobody fails on.
- `<AnalysisLevel>`, which selects the warning wave and therefore which
  diagnostics exist at all.

With all three set, `dotnet build -warnaserror` is a real lint verb. With none,
the same command passes on code the analysers have opinions about, and reports
nothing.

So the C# pack's most useful output is frequently a statement about
configuration, and no list of findings: _this repository has nullable disabled,
so the compiler is not checking the thing it could check_. No diagnostic can
carry that, because no diagnostic is produced.

Analyser packages - Roslynator, Meziantou.Analyzer, SonarAnalyzer, and
`xunit.analyzers` for test-shaped mistakes - are declared once in
`Directory.Build.props`, and never per project.

### Supply-chain checking is built into restore, and its defaults changed in .NET 10

NuGet Audit runs during restore and checks the package graph against
vulnerability databases. Its configuration is MSBuild properties, recommended
at the repository level:

| Property          | Default   | Values                                |
| ----------------- | --------- | ------------------------------------- |
| `NuGetAudit`      | `true`    | `true`, `false`                       |
| `NuGetAuditLevel` | `low`     | `low`, `moderate`, `high`, `critical` |
| `NuGetAuditMode`  | see below | `direct`, `all`                       |

The default that changed is the one a pack must know: _"`NuGetAuditMode`
defaults to `all` when a project targets `net10.0` or higher. Otherwise
`NuGetAuditMode` defaults to `direct`."_ And when a project multi-targets, one
target framework selecting `all` applies it to all of them.

The findings arrive as warnings NU1901 to NU1904 by severity, with NU1900 for a
source that could not be reached and NU1905 for an audit source that provides
no vulnerability database. Those two are what make a naive gate wrong. A
network failure and a misconfigured source are no vulnerabilities, and a build
treating every NU19xx as an error fails for reasons the change never caused.

The documentation gives the pattern directly: warnings as errors only in a
dedicated audit pipeline, through a condition on a property. It also gives the
reason, which is _"preventing new security advisories from blocking your bug
fixes at inconvenient times"_ while developers still see them locally.

Two further tools belong to the same verb. `dotnet list package --vulnerable`
filters to known vulnerabilities, with the documented trap that
_"`--include-transitive` is not default, so should be included"_ - a check
without it reports on a fraction of the graph. And `dotnet package update
--vulnerable`, from NuGet 7.0 with the .NET 10 SDK, updates every vulnerable
package to the first version without a known vulnerability.

When the vulnerability is transitive, `dotnet nuget why` gives the path that
explains it, and the documented preference is to update the package closest to
the direct reference, and never to pin the deep one.

An advisory can be excluded with a `NuGetAuditSuppress` item naming the
advisory URL, which the documentation calls _"a last resort"_. A suppression is
therefore a decision with a reason, which is exactly the shape of a record this
method already has.

Whether the audit ran is itself checkable: restore exposes
`RestoreProjectCount`, `RestoreSkippedCount` and `RestoreProjectsAuditedCount`,
and comparing them in a solution-level target proves every project was audited,
and assumes nothing.

### Testing is mid-migration, and which platform runs matters to the evidence

The framework is one of xUnit, NUnit or MSTest, and they differ in lifecycle
and assertion conventions. xUnit v3 splits into `xunit.v3.core`,
`xunit.v3.assert`, `xunit.v3.common` and separate runners, and its test
projects are stand-alone executables.

Underneath them the runner is changing. Microsoft.Testing.Platform is available
with the .NET 10 SDK and is selected in `global.json`, with VSTest still the
default. The flags differ: the new platform uses `--report-trx` where VSTest
uses `--logger trx`, and `--report-trx` needs the
`Microsoft.Testing.Extensions.TrxReport` package.

That is a direct constraint on evidence. A citable test result is a TRX file,
and which flag produces one depends on a setting in `global.json`, and never on
the test framework. A pack that hard-codes either flag produces a run with no
artifact on half the repositories.

### The release train, and what a preview opt-in means

.NET 10 is the long-term release from November 2025 carrying C# 14. .NET 11 is
a standard-term release with C# 15, expected in November 2026; that timing
comes from secondary coverage and from no release, and is recorded as reported.

The part a reviewer needs is the preview gate. A subset of the next language
version sits behind `<LangVersion>preview</LangVersion>` and the runtime-level
features behind `EnablePreviewFeatures=true`. A repository setting either
depends on something that may change under it.

### What a reviewer needs that no command reports

Nullable reference types treated as errors, and never as suggestions - the
difference between the feature working and the feature being present.

`async` all the way down, and `ConfigureAwait` at a library boundary; both
compile either way and one deadlocks under a synchronisation context.

`IDisposable` and the scope of a `using`, where the defect is a resource held
longer than intended, and never one leaked outright.

Records and value equality, where the meaning of `==` changed at the
declaration and nothing at the call site says so.

Central package management: whether versions are in one file or scattered, and
whether transitive pinning is in use, which changes what the project publishes
if it is itself packed.

Which test framework's conventions apply, because a reader assuming xUnit's
lifecycle in an NUnit project reviews the wrong thing.

### What the skill has to contain

The skill is the pack's body, and the budget is the constraint: the obligations
have to be in the part that survives compaction, and everything else moves to
supporting files.

In the body, in this order:

1. Detection. The nine markers above and what each one means, including
   that `global.json` pins the SDK and that a filter is a subset.
2. The verbs, with their conditions. Not a command table but a resolution:
   `fmt` by detecting CSharpier against `dotnet format`; `lint` as the compiler
   under three settings; `test` with the flag chosen by the configured
   platform.
3. What to read before reporting a pass. Nullable, warnings as errors,
   analysis level, audit mode. This is the part that distinguishes a green run
   from a checked repository, and it is the obligation that goes missing first.
4. What must never happen. Running the other formatter. Hard-coding a TRX
   flag. Treating NU1900 or NU1905 as a vulnerability. Reporting `dotnet list
package --vulnerable` without `--include-transitive`.

In supporting files:

- The authoring templates: a `Directory.Build.props` with the three settings, a
  `Directory.Packages.props`, an audit-pipeline condition, a solution-level
  target asserting every project was audited.
- The analyser package list with what each adds.
- The per-framework test conventions for xUnit, NUnit and MSTest.
- The dated facts, with the date and what to re-check: the solution default,
  the audit mode default, the testing platform's default, the release train.

The review knowledge is the part of the body that cannot be generated from
documentation, and it is what makes this a skill, where a command table would
carry none of it.

## Conclusions

1. A .NET project is detected by `*.slnx`, `*.sln`, `*.slnf` and `*.csproj`
   together, and detecting only `*.sln` misses every solution created by .NET
   10 or later and every solution filter. 2. `global.json` is read before any
   verb runs, because it pins the SDK and, from .NET 10, selects the test
   platform, and a verb run under a different SDK reports on a toolchain nobody
   uses. 3. An unmigrated solution is reported, and migrated never, since
   `dotnet sln migrate` exists and the choice belongs to the repository. 4.
   `fmt` is resolved by detecting CSharpier against `dotnet format` through a
   `.csharpierrc` or a `csharpier` entry in the local tool manifest, because
   running the other one reformats the entire repository. 5. Where a repository
   has chosen no formatter, the pack proposes one and writes nothing, since the
   opinionated tool removes an argument and adds an unsupported dependency, and
   that trade belongs to the project. 6. `lint` resolves to the compiler with
   warnings as errors against the declared analyser set, because .NET has no
   separate linter. 7. The pack reads `Nullable`, `TreatWarningsAsErrors` and
   `AnalysisLevel` before reporting a clean lint, and reports a missing one as
   a finding, because no diagnostic can say that no diagnostic was produced. 8.
   The analyser set and the build policy are declared once for the repository,
   in `Directory.Build.props`, and never per project. 9. Supply-chain checking
   runs as part of restore and its configuration is read, and assumed never:
   `NuGetAuditMode` defaults to `all` on `net10.0` and later and to `direct`
   below it, and one multi-targeted framework selecting `all` applies it to
   all. 10. NU1900 and NU1905 are not vulnerabilities, and a gate that fails on
   every NU19xx fails for an unreachable source or a misconfigured audit
   source, and never for a defect. 11. Audit findings fail a dedicated
   pipeline, and never every build, which is the arrangement the documentation
   gives, so a new advisory does not block an unrelated change while developers
   still see it locally. 12. `dotnet list package --vulnerable` is always run
   with `--include-transitive`, because the flag is not the default and the
   result without it covers a fraction of the graph. 13. A transitive
   vulnerability is traced with `dotnet nuget why` and fixed at the package
   closest to the direct reference, which is the documented preference. 14. A
   suppressed advisory is a recorded decision with a reason, since the
   documentation calls suppression a last resort and the suppression names an
   advisory URL. 15. That the audit ran is itself checked, by comparing
   `RestoreProjectsAuditedCount` against `RestoreProjectCount`. 16. The TRX
   flag is chosen from the configured platform, `--report-trx` for
   Microsoft.Testing.Platform against `--logger trx` for VSTest, because
   evidence is a file and hard-coding either produces runs with none. 17. A
   preview language or runtime opt-in is reported, since
   `<LangVersion>preview</LangVersion>` and `EnablePreviewFeatures=true` mean
   the repository depends on something that may change. 18. A release timing
   taken from secondary coverage is marked as reported. 19. The skill body
   carries detection, conditional verb resolution, what to read before
   reporting a pass, and the prohibitions, in that order, because that is what
   has to survive compaction. 20. Templates, analyser lists, per-framework test
   conventions and dated facts live in supporting files, each dated with what
   to re-check.

## Sources

All read 2026-09-20.

- [`dotnet sln` command
  reference](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-sln) -
  `dotnet new sln` creating an `.slnx` where .NET 9 and earlier created `.sln`;
  every subcommand accepting `.sln`, `.slnx` or `.slnf`; `dotnet sln migrate`
  generating an `.slnx` and failing where one exists; and solution filter
  creation from .NET 11. - [Auditing package dependencies for security
  vulnerabilities](https://learn.microsoft.com/en-us/nuget/concepts/auditing-packages)
  - `NuGetAudit`, `NuGetAuditLevel` and `NuGetAuditMode` with their defaults
    and values; that audit mode defaults to `all` on `net10.0` and later and to
    `direct` otherwise, and that one multi-targeted framework selecting `all`
    applies it to all; warnings NU1900 to NU1905 and what each means; the
    dedicated-audit-pipeline pattern with its stated reason; `NuGetAuditSuppress`
    as a last resort naming an advisory URL; audit sources in `nuget.config` and
    the vulnerability-only endpoint; `dotnet nuget why` for the transitive path
    and the preference for updating the closest package; `dotnet package update
--vulnerable` from NuGet 7.0 with the .NET 10 SDK; the restore output
    properties `RestoreProjectCount`, `RestoreSkippedCount` and
    `RestoreProjectsAuditedCount`; and that `--include-transitive` is not the
    default for `dotnet list package --vulnerable`. - [About
    CSharpier](https://csharpier.com/docs/About) - an opinionated formatter for
    C# and XML whose printing was ported from Prettier; the option philosophy of
    a few basic options and no plans for more; installation as a tool and `dotnet
csharpier format .`; and the check mode for verification. - [DotNet-Format
    against
    CSharpier](https://levelup.gitconnected.com/dotnet-format-vs-csharpier-which-auto-formatting-tool-is-best-for-your-net-code-5376dbe9be20)
  - that CSharpier parses with Roslyn and re-prints while `dotnet format`
    depends on MSBuild and may fail on older project types; that `dotnet format`
    is official and in the SDK while CSharpier is third-party and unsupported by
    Microsoft; and the resulting selection advice. Recorded as a secondary
    source. - [Migrating from VSTest to
    Microsoft.Testing.Platform](https://learn.microsoft.com/en-us/dotnet/core/testing/migrating-vstest-microsoft-testing-platform)
  - the platform available with the .NET 10 SDK and selected in `global.json`
    with VSTest still the default, and `--report-trx` replacing `--logger trx`
    with the `Microsoft.Testing.Extensions.TrxReport` package required. - [What's
    new in xUnit.net v3](https://xunit.net/docs/getting-started/v3/whats-new) -
    the split into `xunit.v3.core`, `xunit.v3.assert`, `xunit.v3.common` and
    separate runners; stand-alone executable test projects; and support for the
    new testing platform. - [What's new in C#
    15](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-15) and
    [Microsoft delivers first preview of .NET 11 and C#
    15](https://www.devclass.com/development/2026/02/13/net-train-keeps-rolling-with-first-showing-of-2026-release/4090277)
  - the features gated behind `<LangVersion>preview</LangVersion>` and
    `EnablePreviewFeatures=true`, and the expected November 2026 release,
    recorded as reported.
