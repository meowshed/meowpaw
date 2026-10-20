<role>
What a reviewer of Starlark checks that no command reports. Read it when you
review a `BUILD`, `.bzl` or `MODULE.bazel` file, after `status` has named the
build system. A clean buildifier run says the formatter and linter found
nothing in what they check, and each point here asks what they can't see.
</role>

<rules name="reviewing Starlark">
- R1. Look for a module-level value mutated after load, because values freeze
  once a module executes and the mutation works only during load.
- R2. Look for recursion, because the language forbids a function calling
  itself and the host may fail late.
- R3. Look for anything reading a clock, a file system or an environment,
  because it is a host builtin or a defect, and the language exists so that
  code can't.
- R4. Name the build system that evaluates the file, because a function that
  formats cleanly can be missing from its builtins.
- R5. Check each `load()` against the host, because resolution differs and a
  copied snippet stops working there.
- R6. Ask whether a macro should have been a rule, because the recurring design
  question has no tool.
- R7. Read a file that is Python-shaped as Starlark, because it has no
  user-defined types, no exceptions, no reflection and no iterable strings.
</rules>
