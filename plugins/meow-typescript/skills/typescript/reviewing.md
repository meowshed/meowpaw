<role>
What a reviewer of TypeScript or JavaScript checks that no command reports.
Read it when you review code, after the package manager and the configured
tools are known. A clean lint and a passing type check say the code meets the
rules the project turned on, and each point here asks about a rule it didn't.
</role>

<rules name="reviewing TypeScript">
- R1. Read the `strict` family in `tsconfig.json` and name each flag left off,
  `noUncheckedIndexedAccess` first, because it is the flag that changes real
  code: it turns every indexed read into a value that may be absent.
- R2. Look for `any`, `as` casts and `@ts-ignore` comments, because they are
  the places type safety is lost, and the compiler stays silent about them by
  design.
- R3. Check the `exports` map of a package that publishes, and whether the
  package claims ESM, CommonJS or both and is wrong about one, because the
  failure appears in the consumer's build after a release.
- R4. Look for a promise nobody awaited or returned, because it fails by not
  happening and no type error reports it.
- R5. Ask which runtime the code targets, because the same source is correct
  in a browser and wrong in Node.
- R6. Name the coverage provider, `v8` or `istanbul`, before comparing a
  percentage, because the two count differently.
- R7. Ask whether a package that publishes ran `publint` for the shape of its
  exports, `arethetypeswrong` for the types a consumer resolves and `knip` for
  dead weight, in that order, because none of the five stages covers them.
- R8. Note when no `dependency-cruiser` or `madge` configuration exists, and
  say the repository has no mechanical architecture check, because the check
  is cheap and almost nobody has it.
</rules>
