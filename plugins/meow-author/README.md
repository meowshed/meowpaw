---
reader: someone choosing or running meow-author
answers: what meow-author does, what it adds to a session and how to run it
kind: reference
describes: [meow-author@0.10.0]
description: "Holds how Claude Code writes skills, agents, output styles, commands and prompt hooks, checks them in a repository's plugins or its own .claude directory for fixed tags, a description, the six fields an agent declares, every supporting file named and a stated stopping point."
---

# meow-author

`meow-author` holds how Claude Code writes skills, agents, output styles,
commands and prompt hooks, and checks what you write, in a plugin or in your
repository's own `.claude/`, for the form the `meowpaw` harness holds its own
units to. Its launcher runs the shared `paw` binary `meow-core` ships.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-author@meowpaw
```

Installing this unit also enables `meow-core`, which ships the shared `paw` binary its launcher runs, and the platform keeps `meow-core` enabled while this unit is on, so you can't disable `meow-core` alone.

Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions, because the unit's behaviour was never seen on an older one.

## What it adds to a session

<!-- host-specific: claude -->

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

<!-- host-specific: claude -->

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
- a description whose first sentence carries none of the words its
  `when_to_use` writes in code font, because a request reaches a unit through
  those words; a unit with no `when_to_use` is not read by this rule;
- an agent that leaves out one of the six fields below, or holds a value the
  table doesn't accept, naming the file and the field;
- an agent whose front matter doesn't parse, with that reason alone, because
  no field can be read from it;
- a plugin shipping a `commands/` directory, where a command is a skill only
  a person invokes;
- a plugin with no version in its `.claude-plugin/plugin.json`, where every
  unit the harness ships carries one;
- a plugin with no `requires.toml`, no `layer`, no `units`, a pack with no
  `kernel` range, or a layer outside kernel, method, practice and pack, where
  the manifest states what the unit ships in and what it needs;
- a README that names a unit in `units` and doesn't say the platform enables
  that unit and keeps it enabled while the first stays on, because a
  required unit can't be turned off alone;
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

## What it checks in a hook

<!-- host-specific: claude -->

For each `hooks/hooks.json` under `plugins/`, and each script a declaration
runs, `meow-author check` fails a hook, naming the file and the event, that:

- answers `allow` as its decision, or returns an `updatedInput`, because a
  hook that approves skips the permission flow the repository owns and one
  that rewrites a call runs something nobody asked for;
- names a network command, such as `curl`, `wget`, `ssh`, `gh`, `git fetch`,
  `git pull` or `claude -p`, except `meow-prose-gate check`, which is excused
  by unit and subcommand and no other hook inherits, and only for its judge's
  `claude -p` while its hook declares a `timeout` of at most 120 seconds;
- is not the unit's launcher with one subcommand, on any event but
  `SessionStart`, `SessionEnd`, `PostToolUse` and `PostToolUseFailure`, so an
  event added later is held to the rule until the check lists it;
- has no sentence under its unit's README `## Hooks` naming the subcommand in
  code font.

A hook that builds a network call at run time is invisible to the check, and
review holds it.

## What it checks in the tools a unit grants

Each tool an agent's `tools` or a skill's `allowed-tools` grants must have a
step named beside it in the unit's README, under `## Tools`, as a list item
that opens with the tool in code font, a colon and what the step does with it.
A tool with no such item fails the check, naming the file, the tool and the
README, so a tool no step needs is visible and removed.

## What each unit loads

`meow-author check` also reads each unit's always-loaded material, and fails
on a skill's or agent's description and its `when_to_use` together over the
platform's cap of 1,536 characters, which the platform sets. How
often each skill is used comes from `/skill-doctor` in Claude Code; the unit
reads none of Claude Code's own files.

## What it costs you The

check is a native binary shipped inside
the unit, so it needs nothing installed on the machine.

## Read a subcommand's help

`meow-author --help` lists the subcommands, and `meow-author <subcommand> --help` names
what it determines, what you read to reach the same answer without the tool,
and the first word of each kind of line it prints. A test holds each
subcommand's output to those words.

## What it needs

<!-- host-specific: claude -->

Claude Code 2.1.283 or later, the version this unit was tested on, declared in
`plugins/meow-author/requires.toml`.
