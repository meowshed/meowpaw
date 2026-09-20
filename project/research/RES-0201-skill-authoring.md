---
id: RES-0201
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0005, RES-0004
---

# The `skill-authoring` skill

## Summary

The authoring surface moved since this project last read it. A command and a
skill are one artifact shape, and how it may be invoked is a frontmatter
decision. Two fields are cheap precision nobody uses - activation scoped to
matching paths, and a forked context for a skill that reads a great deal. Shell
injection aborts the whole invocation on a non-zero exit and can be disabled
outright, so a skill never depends on it.

Research for the skill that writes the others. It covers how a skill, a command
and an agent definition are built, what the platform actually supports, and
what a budget means when every line is a recurring cost.

It covers the authoring surface as it currently stands, which has moved since
this project's earlier reading, and the rules that follow from it.

It does not cover what a skill costs in tokens, which is measured in
[RES-0005-skill-format.md](RES-0005-skill-format.md), nor the platform in
general, which is [RES-0004-platform.md](RES-0004-platform.md).

## The question

Without this skill the harness can be extended only by its authors. Every other
skill in the harness is written with it, including itself, which makes it the
one place where getting the format wrong is multiplied by everything else.

## Method

We fetched and read the platform's documentation on skills and on commands on
2026-09-20, in full and not only for the fields already known. That is how the
newer frontmatter options and the injection failure modes turned up.

The measured budgets are not re-derived here; they come from the separate
skill-cost research, which we cite and repeat none of.

Nothing was authored and measured. No skill was written to this guidance and
evaluated, so the ordering rules rest on the documented compaction behaviour,
and on no result of ours.

## Findings

### Commands and skills are now one mechanism

A custom command is a skill. The documentation states it directly - custom
slash commands are implemented as skills - and the two share a frontmatter
vocabulary.

That collapses a distinction this project's earlier reading treated as real,
and it simplifies the authoring rule. One artifact shape exists, and whether a
person invokes it, the model does, or both do, is a property set in the
frontmatter.

### The frontmatter vocabulary, and which fields are decisions

| Field                      | What it decides                                                 |
| -------------------------- | --------------------------------------------------------------- |
| `description`              | When the model invokes it; stays in context every turn          |
| `name`                     | The display label; for a plugin skill it also names the command |
| `disable-model-invocation` | `true` means only a person may invoke it                        |
| `user-invocable`           | `false` means only the model may, hidden from the menu          |
| `allowed-tools`            | Tools pre-approved for the invoking turn only                   |
| `disallowed-tools`         | Tools removed from the pool while the skill is active           |
| `paths`                    | Glob patterns limiting when it auto-activates                   |
| `context`                  | `fork` runs it in an isolated subagent context                  |
| `arguments`                | Named arguments, referenced as `$name`                          |
| `argument-hint`            | The autocomplete hint                                           |
| `model`, `effort`          | Overrides for the invocation                                    |

Four of these are design decisions, and no setting anybody flips.

`disable-model-invocation` is the control for a command with side effects.
A command that commits, pushes or files something is invoked by a person.

`user-invocable: false` is its mirror, and it is the right setting for a skill
that carries knowledge and performs no action: a reviewer's lens, a language's
idioms. The model reaches for those, and a person has no reason to type them.

`paths` is the cheapest precision available: a language pack's skill that
activates only where that language's marker exists costs nothing elsewhere.

`context: fork` is what makes a skill that reads a great deal - a review
over a large diff, a search across a corpus - affordable, because the reading
stays out of the main context.

### The description is the only part that is always paid for

Progressive disclosure is the mechanism: descriptions load into context every
turn so the model knows what exists, and the body loads only when the skill is
invoked.

So the description is a permanent cost and the body is an occasional one. Two
rules follow.

The description says when to use the skill, and never what it contains. A
description that summarises the body wastes the permanent budget describing
something that will be loaded anyway.

The key use case goes first. The combined description and when-to-use text
is capped at 1,536 characters in listings, and what exceeds it is truncated, so
the discriminating sentence cannot be at the end.

### The body has a stated ceiling and a real one

The documented guidance is to keep `SKILL.md` under 500 lines and move detailed
reference material to supporting files. The reason is stated plainly: skill
content persists across turns, so every line is a recurring token cost.

The real ceiling is tighter, and what decides it is what survives compaction,
where fitting is easy. The obligations go in the part of the body that is read
first, because that is what remains present when the context is compacted.
Explanations, tables, templates and examples move to supporting files, which
are referenced by link so the model knows what it can load and pays nothing
until it does.

That gives the shape every skill in this harness uses: **obligations first,
then the conditional resolution, then the prohibitions**, with everything
discursive behind a link.

### Dynamic context injection is powerful and has three sharp edges

A command may run shell before the model sees it, with `` !`command` `` inline
or a fenced `!` block, and the output replaces the placeholder.

The edges, all documented:

- **A non-zero exit aborts the entire invocation.** So a command that injects
  `git status` in a directory that is not a repository does not degrade - it
  fails before it starts.
- **The timeout is two minutes per command.** An injected test run is a command
  that will sometimes exceed it.
- **It can be disabled.** `disableSkillShellExecution` in settings turns the
  mechanism off, so a skill that depends on injection has to work without it or
  say that it cannot.

The consequence for this harness is that injection carries cheap, certain
context: the current diff, the branch name. It never carries anything that runs
a verb, which belongs in the body as an instruction.

### Variables and paths

`${CLAUDE_PROJECT_DIR}`, `${CLAUDE_SESSION_ID}`, `${CLAUDE_SKILL_DIR}` and
`${CLAUDE_EFFORT}` are substituted in the body.

`${CLAUDE_SKILL_DIR}` is the one a pack needs. A skill's supporting files are
addressed relative to it, so a skill ships a script or a template and
references it knowing nothing about where it was installed.

### Name resolution is a precedence order, and a plugin is the lowest

Enterprise beats personal beats project, a personal skill overrides a bundled
one, and a plugin skill is invoked as `/plugin:skill` or by its short name when
nothing conflicts. A nested skill in a monorepo is qualified by its path.

For a harness distributed as plugins, this decides a naming rule: **every
command is namespaced**. The short name is available only by luck, and a
harness whose commands sometimes collide behaves according to what else is
installed.

### `allowed-tools` cannot pre-approve what is resolved at run time

The grant applies only during the turn that invoked the command, and the rest
of the permission settings still govern.

This costs this harness real friction, and no detail hides it. A gate runs a
command resolved from a profile or a pack at run time, and a static allow list
cannot name it. The honest answer is that a repository pre-approves its own
gate commands in its own permission settings, which the initialisation step can
propose and cannot impose.

## Conclusions

1. A command and a skill are one artifact shape, and how it may be invoked is a
   frontmatter decision that no separate kind of file carries. 2. The
   description says when to use the skill, and never what it contains, because
   it is the only part paid for on every turn. 3. The discriminating sentence
   comes first, since the listing truncates at 1,536 characters. 4. Obligations
   come first in the body, then conditional resolution, then prohibitions,
   because that order survives compaction. 5. Everything discursive moves to a
   supporting file referenced by link, so it costs nothing until it is needed. 6. A body is kept well under the documented 500 lines, since content
   persists across turns and every line recurs. 7. A skill with side effects
   sets `disable-model-invocation`, and a skill that carries knowledge and
   performs no action sets `user-invocable: false`. 8. A skill scoped to a
   language or a directory declares `paths`, which is the cheapest precision
   available. 9. A skill that reads a great deal declares `context: fork`, so
   the reading stays out of the main context. 10. Shell injection is used only
   for cheap, certain context, never for running a verb, because a non-zero
   exit aborts the invocation and the timeout is two minutes. 11. A skill does
   not depend on shell injection, since the mechanism can be disabled in
   settings. 12. Supporting files are addressed through `${CLAUDE_SKILL_DIR}`,
   so a skill works wherever it was installed. 13. Every command the harness
   ships is namespaced, because an unqualified name is available only when
   nothing else claims it. 14. A run-time-resolved command cannot be
   pre-approved by `allowed-tools`, so the repository declares its own
   permissions, and the harness proposes them and imposes none. 15. This skill
   is written with itself, which is the only check that it is usable by someone
   who is not its author.

## Sources

All read 2026-09-20.

- [Skills](https://code.claude.com/docs/en/skills) - skills as bundled
  instructions and supporting files loaded on invocation; the frontmatter
  fields `name`, `description`, `disable-model-invocation`, `allowed-tools`,
  `disallowed-tools`, `user-invocable`, `paths` and `context: fork`;
  progressive disclosure with descriptions in context every turn and bodies
  loaded on invocation; the location precedence of enterprise, personal,
  project, nested and plugin; supporting files referenced from `SKILL.md`; the
  1,536-character cap on the combined description; the guidance to keep
  `SKILL.md` under 500 lines; and the statement that content persists across
  turns so every line is a recurring cost.
- [Slash commands](https://code.claude.com/docs/en/slash-commands) - custom
  commands implemented as skills; `argument-hint`, `model`, `effort` and named
  `arguments`; `$ARGUMENTS` and positional substitutions; shell injection with
  `!` inline and in fenced blocks, running in the session's working
  directory, with a non-zero exit aborting the invocation, a two-minute
  timeout, and the `disableSkillShellExecution` setting; the variables
  `${CLAUDE_SESSION_ID}`, `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_SKILL_DIR}` and
  `${CLAUDE_EFFORT}`; command name resolution and namespacing; and
  `allowed-tools` granting only for the invoking turn.
- [RES-0005-skill-format.md](RES-0005-skill-format.md) - the measured budgets
  and the argument for one skill per discipline.
