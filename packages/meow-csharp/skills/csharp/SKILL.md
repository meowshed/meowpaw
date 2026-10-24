---
name: csharp
description: The stages a C# repository binds, the SDK it pins and the settings that decide whether its lint means anything, and what a reviewer of C# checks. It MUST be loaded before binding a stage in, reporting the toolchain of, or reviewing code in a repository holding a .NET solution or project. It MUST NOT be used to write the profile or a project file.
---

<role>
You read what a .NET repository configured through the pack's program, and you
report what it printed. The program binds each stage from the files the
repository commits and runs no .NET tool, so its table is a proposal the
person accepts, never a result. Three stages are the same compiler with
different arguments, and what decides whether they mean anything is the
configuration, so you report the configuration as well as the commands.
</role>

<steps name="read the configuration">
1. Run `meow-csharp status` and show its output.
2. If it exits 3, report each line starting `unresolved:` as it stands, and
   stop.
3. Otherwise report, for each directory, the target, the pinned SDK, the test
   runner, the formatter and the analysis level, and stop.
</steps>

<steps name="bind the stages">
1. Run `meow-csharp bind` and show the table it
   prints, each comment included.
2. Give the table to the person to put in `.meowpaw/profile.toml`, and stop.
</steps>

<steps name="check the settings">
1. Run `meow-csharp check` and show each
   finding.
2. Report each finding with the file that would set it, and stop.
</steps>

<steps name="review C#">
1. Run `meow-csharp status` for the analysis
   level and the test runner.
2. Read `reviewing.md` before you review C# code, and
   hold the change to each point in it.
3. Report each finding as the line, what is wrong and what would fix it, and
   stop.
</steps>

<rules name="the stages">
- C1. Never guess a command for a stage the program printed as unresolved or
  unbound, because a guessed command turns a settled "nothing" into a pass
  nobody checked.
- C2. Write the profile, a project file or `Directory.Build.props` only when
  the person asks, because each is the repository's declaration.
- C3. Restore in a step of its own and pass `--no-restore` after it, and pass
  one `--artifacts-path` outside the working tree to every `dotnet` command
  that builds, because each command otherwise restores again, and `bin` and
  `obj` otherwise land beside every project.
- C4. Report a clean lint together with the analysis level it ran at, and
  where `check` reports Nullable, TreatWarningsAsErrors or AnalysisLevel
  missing, say the compiler isn't checking what it could, because no
  diagnostic can say that no diagnostic was produced.
- C5. Name what the pack is current as of, the .NET 10 SDK and CSharpier's
  `check` command, read from their documentation on 2026-10-13 and not
  observed running, and where the installed SDK is newer, say a binding may be stale,
  because a default such as the test runner changes under the same command.
</rules>

<rules name="what must never happen">
- C6. Never run `dotnet format` where the repository configured CSharpier, or
  CSharpier where it didn't, because the other formatter reformats the whole
  repository.
- C7. Never turn on `-warnaserror`, an analysis level or a nullable context
  the repository didn't set, because the findings that result are
  preferences the reader can't tell from defects, and they fail the build.
- C8. Never report NU1900 or NU1905 as a vulnerability, because the first is
  a source that couldn't be reached and the second an audit source with no
  vulnerability data.
- C9. Never report `dotnet list package --vulnerable` without
  `--include-transitive`, because the flag isn't the default and the result
  without it covers part of the graph.
</rules>
