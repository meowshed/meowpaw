<role>
What a reviewer of Python checks that no command reports. Read it when you
review code, after the environment and the configured tools are known. A clean
lint and a passing type check say the code meets the rules the project turned
on, and each point here asks about a rule it didn't.
</role>

<rules name="reviewing Python">
- R1. Ask whether the typing is checked or decorative, because annotations no
  configured checker reads look like a typed codebase and are comments.
- R2. Look for import-time side effects, because they make the order of
  imports part of the program's meaning.
- R3. Look for mutable default arguments, because the defect survives every
  review that reads for something else.
- R4. Check the scope of each pytest fixture and whether `pytest-randomly` is
  installed, because a wrongly scoped fixture makes tests pass in one order and
  fail in another.
- R5. Ask whether the package imports from a clean environment, because
  packaging defects live there and no test in the repository looks.
- R6. Name the interpreter versions the package claims and whether anything
  ran on them, because a suite that passes on the developer's interpreter says
  nothing about the others.
- R7. Note when no `import-linter` or `tach` configuration exists, and say the
  repository has no mechanical architecture check, because the check exists and
  almost no project has one.
- R8. Note when `deptry` or `vulture` isn't configured, and say nothing checks
  for a dependency declared and unused, or used and undeclared, or for
  definitions nothing references.
</rules>
