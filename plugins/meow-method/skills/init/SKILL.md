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
3. Write `.meowpaw/profile.toml` from the template, filling each value from
   what the repository already does and leaving out what it doesn't do.
4. Where the repository has no `CLAUDE.md`, write one from the template
   `${CLAUDE_SKILL_DIR}/../../bin/meow-method template constitution` names,
   holding only what the repository already shows. Where it has one, leave it
   untouched and say so.
5. Report the two files, what each value came from, and what you couldn't
   determine.
</steps>

<rules name="initialise">
- N1. Write `.meowpaw/profile.toml` and, only where none exists, `CLAUDE.md`,
  and nothing else: no unit of work, no verb run, nothing installed that
  changes what another tool does, and no edit to a file the repository
  already keeps, because the repository agreed to the harness and to nothing
  more.
</rules>
