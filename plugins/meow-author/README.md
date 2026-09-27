---
reader: someone choosing or running meow-author
answers: what meow-author does, what it adds to a session and how to run it
kind: reference
describes: [meow-author@0.1.0]
---

# meow-author

`meow-author` checks the skills, agents, output styles and prompt hooks you
write for Claude Code, in a plugin or in your repository's own `.claude/`, for
the form the `meowpaw` harness holds its own units to. It installs on its own,
with no other part of the harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-author@meowpaw
```

## Run the check

Claude Code puts the unit's `bin/` directory on its Bash tool's `PATH`. Run
the check on your repository's own material:

```bash
meow-author check .claude
```

With no path it reads every plugin under `plugins/`. It fails, naming the
file and the line, on:

- a Markdown heading, a tag outside `<role>`, `<rules>`, `<steps>`,
  `<example>` and `<input>`, a tag opened inside another, a tag never closed,
  or text outside every tag;
- a skill or agent with no `description`;
- a plugin shipping a `commands/` directory, where a command is a skill only
  a person invokes;
- a file in a skill's directory that its `SKILL.md` never names;
- a path climbing out of a file with no directory variable in front of it,
  such as the platform's variable for the skill's or the plugin's directory;
- a skill or agent whose procedure never says where it stops.

It exits 0 when it finds nothing, 1 on a finding, and 3 when there is nothing
to check or its binary is missing for your machine.

## What it costs you

Nothing in context on every turn. The check is a native binary shipped inside
the unit, so it needs nothing installed on the machine.

## What it needs

Claude Code 2.1.283 or later, the version this unit was tested on, declared in
`plugins/meow-author/requires.toml`.
