---
name: markdown
description: The verbs a Markdown repository binds and what its configuration says. It MUST be loaded before binding a verb in, or reporting the tools of, a repository whose Markdown documents are checked. It MUST NOT be used to write the profile or a tool's configuration.
---

<role>
You read what a repository configured for its Markdown through the pack's
program, and you report what it printed. The program binds each verb from the
files the repository commits, and its binding runs none of the tools it names,
so its table is a proposal the person accepts, never a result.
</role>

<steps name="read the configuration">
1. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-markdown status` and show its
   output.
2. If it exits 3, report the line starting `unresolved:` as it stands, and
   stop.
3. Otherwise report the render target and each configuration file with what
   reads it, and stop.
</steps>

<steps name="bind the verbs">
1. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-markdown bind` and show the table
   it prints, each comment included.
2. Give the table to the person to put in `.meowpaw/profile.toml`, and stop.
</steps>

<rules name="markdown">
- M1. Never guess a command for a verb the program printed as unresolved or
  unbound, because a guessed command turns a settled "nothing" into a pass
  nobody checked.
- M2. Write the profile only when the person asks, because the profile is the
  repository's declaration.
</rules>
