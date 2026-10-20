<role>
What a reviewer of C# checks that no command reports. Read it when you review
C# code, after `status` has named the analysis level and the test runner. A
clean build says the compiler found nothing at the level it ran at, and each
point here asks what that level can't see.
</role>

<rules name="reviewing C#">
- R1. Check that nullable warnings are errors and not suggestions, because a
  nullable context whose warnings nobody fails on is the feature present and
  not working.
- R2. Check that `async` runs all the way down and that a library boundary
  uses `ConfigureAwait(false)`, because both compile either way and one
  deadlocks under a synchronisation context.
- R3. Check the scope of each `using` against how long the resource is
  needed, because the defect is a resource held longer than intended, which
  no analyser reports as a leak.
- R4. Check what `==` means on each record and value type a change
  compares, because a record declaration changes equality and nothing at the
  call site says so.
- R5. Check that package versions sit in `Directory.Packages.props` and that
  transitive pinning is deliberate, because scattered versions change what
  the project publishes when it is packed.
- R6. Read the test framework's conventions before reviewing a test, because
  xUnit, NUnit and MSTest differ in lifecycle, and a reader assuming one
  reviews the wrong thing in another.
- R7. Report `<LangVersion>preview</LangVersion>` or
  `EnablePreviewFeatures`, because the repository then depends on something
  that may change under it.
- R8. Report a solution still in the `.sln` format as one `dotnet sln migrate`
  would make reviewable, and never migrate it, because the choice is the
  repository's.
</rules>
