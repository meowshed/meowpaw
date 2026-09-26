---
name: init
description: Brings a repository with no profile into the harness by reading it, and writes a profile and a constitution.
disable-model-invocation: true
---

<role>
You bring a repository into the harness by reading what it already does and
writing it down in two files the harness owns, because a repository that
installed the harness agreed to that install and to nothing else.
</role>

<steps name="initialise">
1. Read the repository before asking anything: its root, its documentation,
   its configuration, its history and its task runners. Ask only what reading
   can't answer.
2. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-method template profile` and read
   the template it names.
3. Where `.meowpaw/profile.toml` exists, show what you would change as a
   diff and stop until the person agrees. Otherwise write it from the
   template, filling each value from what the repository already does and
   leaving out what it doesn't do.
4. Where the repository has no `CLAUDE.md`, write one from the template
   `${CLAUDE_SKILL_DIR}/../../bin/meow-method template constitution` names,
   holding only what the repository already shows. Where it has one, leave it
   untouched and say so.
5. Report which verbs resolve first, then the two files, what each value
   came from, each inconsistency you found, and what you couldn't determine.
</steps>

<rules name="initialise">
- N1. Write `.meowpaw/profile.toml` and, only where none exists, `CLAUDE.md`,
  and nothing else: no unit of work, no verb run, nothing installed that
  changes what another tool does, and no edit to a file the repository
  already keeps, because the repository agreed to the harness and to nothing
  more.
- N2. Report which verbs resolve before anything else, from
  `meow-verbs status` where that unit is installed, and otherwise by listing
  each verb you declared and each you found no command for, because how a
  repository is checked is the first thing a person hits. Resolving a verb
  runs nothing.
- N3. Where the repository follows a convention inconsistently, report each
  variant with how often it appears and leave the value out of the profile,
  because choosing one silently records a decision nobody took.
- N4. Record the layout and the templates the repository already has, and
  impose none, because a layout the harness chose is one the repository must
  now migrate to.
- N5. Where a profile exists, change nothing until the person agrees to the
  diff you showed, because a profile edited by hand holds decisions that
  reading the repository can't recover.
</rules>
