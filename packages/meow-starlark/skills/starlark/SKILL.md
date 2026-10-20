---
name: starlark
description: The stages a Bazel or Buck workspace binds, which build system evaluates its Starlark, and what a reviewer of Starlark checks. It MUST be loaded before binding a stage in, reporting the toolchain of, or reviewing code in a repository holding a MODULE.bazel, REPO.bazel, WORKSPACE, WORKSPACE.bazel or .buckconfig. It MUST NOT be used to write the profile or a tool's configuration.
---

<role>
You read what a Starlark repository configured through the pack's program, and
you report what it printed. The program binds each stage from the files the
repository commits and runs no build tool, so its table is a proposal the
person accepts, never a result. One tool, buildifier, is shared and the host
build system supplies the rest, so the build system comes first and an
unbound stage is the normal state, not a fault.
</role>

<steps name="read the configuration">
1. Run `meow-starlark status` and show its output.
2. If it exits 3, report each line starting `unresolved:` as it stands, and
   stop.
3. Otherwise report, for each directory, what `status` printed, and stop.
</steps>

<steps name="bind the stages">
1. Run `meow-starlark bind` and show the table it prints, each comment included.
2. Give the table to the person to put in `.meowpaw/profile.toml`, and stop.
</steps>

<steps name="review Starlark">
1. Run `meow-starlark status` for what the repository configured.
2. Read `reviewing.md` before you review Starlark code, and hold the change to each
   point in it.
3. Report each finding as the line, what is wrong and what would fix it, and
   stop.
</steps>

<rules name="the stages">
- S1. Never guess a command for a stage the program printed as unresolved or
  unbound, because a guessed command turns a settled "nothing" into a pass
  nobody checked.
- S2. Say which kind of unresolved a stage is: the language has no such thing,
  as with `check`, or the build system isn't identified, because the first
  never resolves and the second might.
- S3. Write the profile, `.buildifier.json` or a `BUILD` file only when the
  person asks, and change a `BUILD` file through `buildozer`, verifying the
  result, because its edits around `select` and variables are reported
  unreliable and unverified.
- S4. Name the sources the pack is current as of, buildifier's source and
  Bazel's documentation as read on 2026-10-13, none observed running, and
  where an installed tool is newer, say a binding may be stale.
</rules>

<rules name="what must never happen">
- S5. Never ask buildifier for `--format=json` in a stage, because it then
  exits 0 whatever it finds.
- S6. Never run buildifier without `--mode=check`, because the default mode
  rewrites the files.
- S7. Never run Bazel without `--symlink_prefix=/`, because the convenience
  symlinks land in the working tree.
- S8. Never treat every `.star` file as Bazel's, because another host embeds
  the language with different functions.
- S9. Never claim a type check, because the language has none.
</rules>
