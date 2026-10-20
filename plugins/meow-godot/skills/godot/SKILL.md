---
name: godot
description: The stages a Godot project binds, which engine version its project file names, and what a reviewer of GDScript and scenes checks. It MUST be loaded before binding a stage in, reporting the toolchain of, or reviewing code in a repository holding a project.godot. It MUST NOT be used to write the profile or a tool's configuration.
---

<role>
You read what a Godot repository configured through the pack's program, and
you report what it printed. The program binds each stage from the files the
repository commits and runs no Godot tool, so its table is a proposal the
person accepts, never a result. The engine supplies three of the stages and a
Python package the other two, so the engine version comes first and an
unbound stage is the normal state, not a fault.
</role>

<steps name="read the configuration">
1. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-godot status` and show its output.
2. If it exits 3, report each line starting `unresolved:` as it stands, and
   stop.
3. Otherwise report, for each directory, what `status` printed, and stop.
</steps>

<steps name="bind the stages">
1. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-godot bind` and show the table it prints, each comment included.
2. Give the table to the person to put in `.meowpaw/profile.toml`, and stop.
</steps>

<steps name="review Godot and GDScript">
1. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-godot status` for what the repository configured.
2. Read `${CLAUDE_SKILL_DIR}/reviewing.md` before you review Godot and GDScript code, and hold the change to each
   point in it.
3. Report each finding as the line, what is wrong and what would fix it, and
   stop.
</steps>

<rules name="the stages">
- G1. Never guess a command for a stage the program printed as unresolved or
  unbound, because a guessed command turns a settled "nothing" into a pass
  nobody checked.
- G2. Write the profile, `project.godot` or `export_presets.cfg` only when the
  person asks, because the engine rewrites `project.godot` and expects its
  ordering.
- G3. Run the import before an export or a headless test run, because
  `--export-release` imports nothing and a clean checkout exports assets
  nobody imported.
- G4. Report a missing engine or missing export templates as an environment
  failure, apart from a failure in the project, because the templates are a
  separate download matched to the engine version.
- G5. Name the versions the pack is current as of, Godot 4.7 and gdtoolkit
  4.x as the research read them in 2026-09, none observed running, and where
  an installed tool is newer, say a binding may be stale.
</rules>

<rules name="what must never happen">
- G6. Never read or print `export_presets.cfg` on an engine older than 4.1,
  because those versions may store credentials in it.
- G7. Never mix gdtoolkit's 3.x and 4.x lines, because the wrong line reports
  parse errors in correct code.
- G8. Never report an untyped script as clean, because the linter doesn't
  require types and the review does.
- G9. Never leave `.godot/` unignored or the `.uid` files ignored, because the
  first fills the history with cache and the second breaks every
  collaborator's scene links.
</rules>
