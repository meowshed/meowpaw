---
reader: someone choosing or running meow-author
answers: what meow-author does, what it adds to a session and how to run it
kind: reference
describes: [meow-author@0.6.1]
---

# meow-author

`meow-author` holds how Claude Code writes skills, agents, output styles,
commands and prompt hooks, and checks what you write, in a plugin or in your
repository's own `.claude/`, for the form the `meowpaw` harness holds its own
units to. It installs on its own, with no other part of the harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-author@meowpaw
```

## What it adds to a session

Before Claude Code creates or edits a skill, an agent definition, an output
style, a command or a hook prompt, it loads the `meow-author:write` skill. The
skill has it declare what the material is for and who invokes it, write the
body in the five tags with every obligation a numbered rule, name every
supporting file, end every procedure at a stopping point, and run the check
before it stops.

For an agent, the skill has Claude Code write out `maxTurns`, `tools`,
`model`, `effort`, `omitClaudeMd` and `skills`, each with the reason the
platform's default is wrong for it. It ships knowledge, such as a language's
idioms, as a skill and never as an agent, because an agent pays for a fresh
context on every dispatch. It never describes a delegated agent as a boundary,
because the agent runs under the parent's sandbox configuration. An output
that comes back marked partial is read as unfinished work.

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
- an agent that leaves out one of the six fields below, or holds a value the
  table doesn't accept, naming the file and the field;
- an agent whose front matter doesn't parse, with that reason alone, because
  no field can be read from it;
- a plugin shipping a `commands/` directory, where a command is a skill only
  a person invokes;
- a file in a skill's directory that its `SKILL.md` never names;
- a path climbing out of a file with no directory variable in front of it,
  such as the platform's variable for the skill's or the plugin's directory;
- a skill or agent whose procedure never says where it stops.

An agent writes out six fields, because the platform has a default for each
one and a default is a value nobody chose:

| Field          | What the check accepts                                    | Why                                                           |
| -------------- | --------------------------------------------------------- | ------------------------------------------------------------- |
| `maxTurns`     | A positive integer                                        | The runner stops the agent there, so a loop can't run forever |
| `tools`        | A list, or a comma-separated string, `[]` included        | An agent holds only the tools someone chose for it            |
| `model`        | `sonnet`, `opus`, `haiku`, `fable` or a `claude-` name    | `inherit` leaves the cost to whichever session dispatches it  |
| `effort`       | `low`, `medium`, `high`, `xhigh` or `max`                 | The effort sets the cost of every turn the agent takes        |
| `omitClaudeMd` | `true` or `false`                                         | It says whether the agent judges by the repository's rules    |
| `skills`       | A list of skill names, `[]` where the agent preloads none | The agent loads its skills, so its dispatcher doesn't         |

In a plugin's `agents/` directory the check also fails a `tools` list holding
`*`, `Agent` or `Task`, alone or with a restriction such as `Agent(worker)`,
because a shipped agent that dispatches another one multiplies the cost the
repository agreed to. Your own agents under `.claude/agents/` may list any
tools, once they write the list.

A plugin's agent also names, in its body, the four outcomes it may end a
dispatch with: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT` and `BLOCKED`. The
check fails one that leaves any of them out, naming each missing word, because
the skill that dispatches the agent acts on that word before it reads the
report. It doesn't read your own agents under `.claude/agents/` for this.
The write skill also has such an agent carry the denial rule: where a tool
call is denied, the agent tries no other way, asks nobody for the permission
and ends as `BLOCKED`, naming the tool and what it was called on. No check
holds that rule.

It exits 0 when it finds nothing, 1 on a finding, and 3 when there is nothing
to check or its binary is missing for your machine.

## Report what each unit costs

`meow-author cost` reports, for each plugin under `plugins/`, the characters it
keeps in context on every turn against the budget its `budget.toml` states:

```bash
meow-author cost
```

It counts each skill's and agent's description and `when_to_use`, and the
whole of each output style, and fails on a plugin over its budget, a plugin
with no `budget.toml`, and a description and its `when_to_use` together over
the platform's cap of 1,536 characters. How often each skill is used comes
from `/skill-doctor` in Claude Code, which the report names; the unit reads
none of Claude Code's own files.

## What it costs you

The skill's description costs 293 characters in context on every turn. The
check is a native binary shipped inside
the unit, so it needs nothing installed on the machine.

## What it needs

Claude Code 2.1.283 or later, the version this unit was tested on, declared in
`plugins/meow-author/requires.toml`.
