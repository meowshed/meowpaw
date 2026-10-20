---
name: scheme
description: The stages a Scheme project binds, which implementation runs it, and what a reviewer of Scheme checks. It MUST be loaded before binding a stage in, reporting the toolchain of, or reviewing code in a repository holding an info.rkt, a .egg file or a guix.scm. It MUST NOT be used to write the profile or a tool's configuration.
---

<role>
You read what a Scheme repository configured through the pack's program, and
you report what it printed. The program binds each stage from the files the
repository commits and runs no Scheme implementation, so its table is a
proposal the person accepts, never a result. A command from the wrong
implementation frequently succeeds and does something else, so the
implementation comes first and an unbound stage is the normal state, not a
fault.
</role>

<steps name="read the configuration">
1. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-scheme status` and show its output.
2. If it exits 3, report each line starting `unresolved:` as it stands, and
   stop.
3. Otherwise report, for each directory, what `status` printed, and stop.
</steps>

<steps name="bind the stages">
1. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-scheme bind` and show the table it prints, each comment included.
2. Give the table to the person to put in `.meowpaw/profile.toml`, and stop.
</steps>

<steps name="review Scheme">
1. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-scheme status` for what the repository configured.
2. Read `${CLAUDE_SKILL_DIR}/reviewing.md` before you review Scheme code, and hold the change to each
   point in it.
3. Report each finding as the line, what is wrong and what would fix it, and
   stop.
</steps>

<rules name="the stages">
- C1. Never guess a command for a stage the program printed as unresolved or
  unbound, because a guessed command turns a settled "nothing" into a pass
  nobody checked.
- C2. Treat every stage as unresolved until the implementation is identified,
  and identify it from a manifest, never from a `.scm` extension, because the
  extension names Scheme and no implementation.
- C3. Write the profile or `info.rkt` only when the person asks, and write no
  portable configuration, because none exists.
- C4. Report Racket's `raco test` result from its summary table and exit status,
  because Racket has no report format to read, and elsewhere report captured
  output and an exit status only.
- C5. Name the sources the pack is current as of, Racket's documentation as
  read on 2026-10-13, none observed running, and where an installed tool is
  newer, say a binding may be stale.
</rules>

<rules name="what must never happen">
- C6. Never run a command from one implementation against another's project,
  because it frequently succeeds and does the wrong thing.
- C7. Never report a zero exit status from an unidentified implementation as a
  pass.
- C8. Never run `raco make` or `raco test --make` in a stage, because they write
  `compiled/` beside each source.
- C9. Never expect `raco fmt` to check, because it prints the formatted program
  or rewrites the file and reports no difference.
- C10. Never claim coverage outside Racket.
</rules>
