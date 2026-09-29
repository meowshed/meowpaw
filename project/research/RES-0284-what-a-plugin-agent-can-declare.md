---
id: RES-0284
artifact: research
status: approved
revised: 2026-09-29
elaborates: RES-0263
---

# A plugin agent declares its turns, tools, model, effort and skills, and a plugin can't set the session's nesting depth

## Summary

Claude Code 2.1.280 reads `maxTurns`, `tools`, `model`, `effort`,
`omitClaudeMd` and `skills` from an agent a plugin ships, so the turn ceiling,
model, effort, instructions and preloaded skills RES-0263 asked a dispatch to
carry can be written in the definition and checked there. The loader also
reads `isolation` and `disallowedTools`, and this note records only that it
reads them, not what each does at a dispatch. Three answers differ from what
RES-0263 assumed. The nesting depth is a variable only settings can set, and a
plugin's own settings keep only `agent` and `subagentStatusLine`, so a plugin
can't set the depth for the session. A plugin can withhold the delegation tool
from each agent it ships, by leaving `Agent`, `Agent(...)` and `Task` out of
that agent's `tools`, which fixes the depth below that agent at none. RES-0263
said the platform withholds the delegation tool at the limit; it doesn't: the
tool stays offered and a call to it fails with an error. `omitClaudeMd` is honoured only when true, so
an agent that leaves it out loads the project's instructions, and a reader
can't tell whether that was a choice. This covers plugin agents only; project
and user agents accept more fields, and this note didn't examine them.

## The question

RES-0263 concluded that the harness sets the nesting depth to one and that
every dispatch declares a turn ceiling, a model, an effort, whether it loads
the project's instructions and the skills it preloads. A decision about what
every shipped agent declares needs to know which of those a plugin can
actually set, what the platform does when a field is missing, and which
values it accepts, because a check that requires a field the platform ignores
checks nothing.

## Method

I read two pages of the platform's documentation on 2026-09-28: the subagent
page and the plugin reference. I then read the agent loader in the installed
binary, Claude Code 2.1.280 at
`~/.local/share/mise/installs/claude/2.1.280/claude`, by extracting its
strings and reading the function that parses a plugin agent's front matter,
the function that resolves an agent's tool list, the table of earlier tool
names and the function that refuses a spawn at the depth limit.

On 2026-09-29 I read the same binary again for three more answers: what the
resolver grants for an empty `tools` list, whether the runner refuses an
agent whose tools resolve to nothing, and what the plugin loader keeps when
`maxTurns` or `effort` is missing.

I dispatched no agent and ran no model, so what the runner does at a limit is
read from the code and the documentation, and no run shows it. The binary is
one version, and the loader can change in the next one.

## Findings

### A plugin can't set the session's nesting depth

The subagent page says a subagent spawns its own subagents up to three layers
below the main conversation by default. It names the variable
`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, set through the `env` table of a
settings file, and says "Set `1` to turn nesting off". In the binary the
default is the constant `3`, a remote feature flag can replace it, and the
variable overrides both. At the limit the Agent tool is still offered, and a
call to it throws "Subagent nesting limit reached", with a message telling the
model to do the work itself. RES-0263 said the platform withholds the tool at
the limit, and the code shows it refuses the call instead.

The plugin reference says a plugin's `settings.json` applies only `agent` and
`subagentStatusLine`, and that other keys are dropped at load. So a plugin has
no way to set the variable, and only the user's or the repository's settings
can.

### Leaving `Agent` out of `tools` withholds delegation from one agent

The subagent page says an agent that omits `tools` inherits every tool, and
that an agent omitting `Agent` from its `tools` list can't spawn subagents.
In the binary, a `tools` value of `*` also means every tool. The delegation
tool is named `Agent` and declares `Task`, its earlier name, as an alias. A
table of earlier tool names maps `Task` to `Agent`, and the parser for a tool
entry applies that table, so a `tools` entry `Task` most likely grants `Agent`.
I didn't confirm that the function resolving an agent's list calls that
parser, so this last step is read from the code and not traced end to end.
The resolver treats an entry such as `Agent(worker)` as the delegation tool
limited to the named agent types, so a restricted entry still delegates.

The resolver grants every tool only when the list is missing or holds `*`.
Otherwise it grants the entries it recognises and nothing else, so an empty
list, `tools: []`, grants no tool, the delegation tool included. The runner
refuses to start an agent whose tools resolve to nothing only when the list
named an entry that matched no tool. An agent whose list is empty starts with
no tools and no error.

### The runner enforces `maxTurns`

The subagent page defines `maxTurns` as the number of agentic turns before
the subagent stops, and says the output then comes back marked as partial,
from version 2.1.246. The binary rejects a value that isn't a positive
integer with "has invalid maxTurns", and its partial marker reads "NOTE: this
agent stopped at its".

The plugin loader copies `maxTurns` onto the agent only when the key is
present. I didn't read what the runner does with an agent that has none,
whether it runs with no ceiling or applies a default, so this note doesn't
show what a missing `maxTurns` costs.

### `omitClaudeMd` is honoured only when true

The subagent page says every custom agent loads the user, project and local
instruction files unless its definition sets `omitClaudeMd`, from version
2.1.271. The plugin loader keeps the field only when it is `true` or the
string `"true"`, so `false` and a missing key behave the same.

### `model` and `effort` are validated, and `inherit` states no model

The subagent page accepts `model` as an alias (`sonnet`, `opus`, `haiku`,
`fable`), a full model identifier or `inherit`, and when the field is missing
the platform picks a model by its own order. An agent on `inherit` runs on the
dispatching session's model, so what a dispatch of it costs is set by
whichever session dispatches it, and the agent's author doesn't choose it. The
page lists `effort` as `low`, `medium`, `high`, `xhigh` or `max`, overriding
the session's level, and says the levels available depend on the model,
without a table of which model offers which level. The binary warns on any
other effort value, and also accepts an integer, which the page doesn't
document. The plugin loader copies `effort` onto the agent only when the key
is present. The page's word "overriding" suggests that an agent without the
key runs at the session's level, but I didn't read the code that picks the
level for a dispatch, so this note doesn't show what a missing `effort` does.

### `skills` preloads, and doesn't restrict

The subagent page says each skill listed in `skills` has its full content
injected at startup, and that an agent can still invoke an unlisted skill
through the Skill tool. So the field controls what the agent pays for up
front, and grants and withholds nothing. The plugin loader reads a missing
`skills` key as an empty list, so an agent that leaves it out preloads nothing,
exactly as `skills: []` does.

### The loader reads `isolation` and `disallowedTools`

The plugin loader keeps `isolation` only when its value is `worktree`, and
reads `disallowedTools` as a tool list in the same form as `tools`. I didn't
read what either does when the agent is dispatched.

### Three fields are ignored in a plugin agent

The plugin loader warns that `permissionMode`, `hooks` and `mcpServers` are
ignored for plugin agents, and tells the author to use `.claude/agents/` for
that control.

## Conclusions

1. A plugin can't set the session's nesting depth, so a harness that ships as
   plugins fixes the depth only for the agents it ships, by leaving the
   delegation tool out of each one's tool list. `Agent`, an entry such as
   `Agent(worker)` and `Task` all count as the delegation tool, so a list
   withholds it only when it names none of the three. That `Task` grants
   `Agent` is read from the code and not traced end to end, and the list
   bans it either way. This note didn't read how the resolver reads an entry
   such as `Task(worker)`. A check that bans every entry named `Agent` or
   `Task`, with or without a parenthesised part, covers it whichever way the
   resolver reads it.
2. An agent the harness ships lists its tools, because a missing list and `*`
   both grant every tool, the delegation tool among them. An empty list grants
   nothing, so it withholds the delegation tool too. A second way to withhold
   the tool is `disallowedTools: [Agent, Task]`, which the loader reads,
   but this note didn't read what it does at a dispatch. This conclusion
   holds only until somebody reads it, and a written `tools` list is the one
   remedy the findings show working.
3. A shipped agent's turn ceiling is `maxTurns`, and a dispatcher reads an
   output marked partial as unfinished work, because the marker means the
   ceiling stopped the agent before it finished, so the output can't be
   treated as complete. The partial marking is read from the code and the
   documentation, and no run has shown it. This note didn't read what a
   missing `maxTurns` does, so it doesn't settle whether a shipped agent has
   to write the key; a decision that requires it rests on RES-0263's
   conclusion that every dispatch declares a ceiling, not on a finding here.
4. A shipped agent states `omitClaudeMd` as `true` or `false`, because the
   platform treats a missing key as `false`, and a reader can tell a choice
   from a default only when the key is written.
5. A shipped agent names a model other than `inherit`, because `inherit` leaves
   the cost to whichever session dispatches it. Its effort is one of the five
   documented levels, and not an integer, because the integer is undocumented
   and the next version may drop it. Whether a named model offers the named
   level is an open question: the page says the levels depend on the model,
   no table says which, and this note didn't read what the platform does with
   a level the model lacks, so a check of the level alone can pass a pairing
   the platform changes or refuses. This note didn't read what a missing
   `effort` does either, so it doesn't settle whether a shipped agent has to
   write the key; a decision that requires it rests on RES-0263's conclusion
   that every dispatch declares an effort.
6. A shipped agent states its `skills`, an empty list included, because the
   platform treats a missing key as an empty list, and a reader can tell a
   choice from a default only when the key is written, as with `omitClaudeMd`.
   Conclusions 4 and 6 ask a check to demand a key whose absence the platform
   treats the same way. That enforces a convention and not a behaviour, which
   is what this note warns against, and it's worth the line it costs, because
   the check can't otherwise tell a deliberate default from a field somebody
   forgot, and a default the platform changes would change every agent that
   left the key out.
7. A shipped agent carries no `permissionMode`, `hooks` or `mcpServers`,
   because a plugin agent ignores all three and a reader would take them as
   enforced.

Conclusion 1 picks withholding the delegation tool from each shipped agent
over the other way the findings name: the harness asking each repository or
user to set `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` to `1` in its own settings.
The variable covers every agent in the session, the built-in ones included,
but it holds only where somebody made the setting, and a repository whose
owner never made it gets none of it. Withholding holds in every repository
with no setup, and it leaves three things unenforced. Agents the harness
doesn't ship, such as the built-in ones and a repository's own, still nest up
to three deep. A project agent overrides a plugin agent of the same name
(RES-0263, conclusion 12), so a repository's replacement can put `Agent` back.
And the depth below a shipped agent is none, where RES-0263 wanted one. The
two match when the harness's own skills dispatch a shipped agent from the main
conversation. They differ when a subagent the harness doesn't ship dispatches
it, because that agent is already one level down. Withholding wins because it
needs nothing from the repository, and the two don't exclude each other: a
repository can still set the variable on top.

Withholding through `disallowedTools: [Agent, Task]` is a third option, and
this note can't weigh it, because it records only that the loader reads the
field. It would leave every other tool granted where a written `tools` list
names each one, and until somebody reads what the field does at a dispatch,
the written list is the option the findings support.

Conclusion 5 moves the choice of model, and with it the cost of each
dispatch, from the person running the session to whoever wrote the agent.
That is the case against naming a model: the person paying no longer chooses
what a dispatch costs, and a session on a cheap model pays for the dearer one
the agent names. Naming a model still wins, because under `inherit` nobody
chose the cost either: it follows whatever model the session happened to run,
and the agent's author, who knows what the work needs, has no say. A person
who disagrees with the named model can replace the agent with a project agent
of the same name (RES-0263, conclusion 12). This note didn't read what the
platform does when the named model or alias isn't offered to the session, for
example through the user's plan or provider, so whether the dispatch fails,
falls back or runs on another model is unread, as the effort-level pairing is.

## Sources

- Read 2026-09-28, [Subagents](https://code.claude.com/docs/en/sub-agents) -
  the default depth of three, `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` and the
  value `1` turning nesting off; a missing `tools` inheriting every tool and
  a list without `Agent` spawning nothing; `maxTurns` and the partial marking;
  `omitClaudeMd` and the instruction files every other agent loads; the model
  values and the order used when none is given; the five effort levels; and
  `skills` preloading without restricting.
- Read 2026-09-28, [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference) - that a plugin's settings apply only `agent` and
  `subagentStatusLine` and drop other keys.
- Read 2026-09-28, the installed Claude Code 2.1.280 binary - the plugin
  agent loader: `omitClaudeMd` kept only when true, `tools: *` as every tool,
  a missing `skills` read as an empty list, `isolation` kept only as
  `worktree`, `disallowedTools` read as a list, the `maxTurns` and `effort`
  validation, and the warning on `permissionMode`, `hooks` and `mcpServers`;
  the depth default of `3`, the variable overriding it and the refusal at the
  limit; the delegation tool named `Agent` with the alias `Task`, the table
  mapping `Task` to `Agent`, and the resolver's reading of `Agent(worker)`;
  and the partial marker.
- Read 2026-09-29, the same binary - the resolver granting every tool only for
  a missing list or `*`, an empty list resolving to no tool, the refusal of a
  zero-tool spawn only when the list named an unmatched entry, and the plugin
  loader copying `maxTurns` and `effort` only when each key is present.

## Open review findings

- The reviewer asked, as a preference, that conclusions 2 and 4 to 7 be
  phrased as findings and not as obligations. I kept the obligation form,
  because RES-0263 writes its conclusions that way and this note elaborates
  it; changing one note alone would leave the two reading differently.
