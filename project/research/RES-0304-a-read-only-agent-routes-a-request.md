---
id: RES-0304
artifact: research
status: approved
revised: 2026-09-28
elaborates: RES-0053, RES-0263
---

# A plugin agent limited to Read, Grep and Glob can't write, and routing through it costs a dispatch per request

## Summary

On Claude Code 2.1.280, dispatched from a non-interactive `claude -p` session
in the foreground, a plugin agent whose front matter sets
`tools: Read, Grep, Glob` holds those three tools and no other. Asked to create
a file, it reported that it had no tool that writes, and the work tree stayed
clean. With `Write` added to the same list, the same brief created the file. So
an allowlist makes "classification writes nothing" a property of the agent's
definition, one that a program can check. An instruction can only ask for it.

The same version lists neither Grep nor Glob among the main session's tools, yet
the subagent held and called both. An allowlist naming them works on 2.1.280,
and depends on the platform keeping them for subagents. An interactive session
is unmeasured, and there RES-0263 reads the documentation as running a subagent
in the background by default with a smaller built-in tool set.

Routing through the agent costs one dispatch on every request it routes. Two
runs in a repository of one file took 12.8 s and 19.7 s end to end, at USD 0.096
and USD 0.053 on Sonnet, after taking out the 3 s the second run spent waiting
on standard input. Nothing here measures how that grows with the
repository or with the request.

## The question

The routing research, RES-0053, concludes that classification reads the request
and the repository, reports before work starts, and writes nothing. Two
questions follow for a design. First, what makes "writes nothing" hold every
time, not only when the model remembers the rule? Second, what does a routed
request cost before the work begins?

The assumption behind both is that classification needs a separate agent at all.
The main session could classify under a skill's instructions and pay no
dispatch. That option is weaker on the first question: the main session holds
Write, Edit and Bash, so only its instructions keep it from writing. It also
carries the conversation that asked for the change, the context in which
RES-0053 found the model that "just fixes it". The agent option has the opposite
weakness: it runs in its own context window (RES-0263), so it sees none of that
conversation and gets only what the brief passes
it, so context the classification needs can be lost in the hand-off. The
findings below measure the agent option and leave the in-context option
unmeasured.

## Method

I ran three sessions on 2026-09-28 with Claude Code 2.1.280, the version
installed on this machine, in a scratch repository holding one committed
`README.md` on a branch named `work`. Each session ran
`claude -p --plugin-dir <plugin> --model sonnet --max-turns 6 --permission-mode acceptEdits --output-format stream-json --verbose`,
and the prompt asked the session to dispatch the agent `probe:router` and print
its reply. Each dispatch ran in the foreground: the main session's second turn
began only after the `tool_result` carrying the agent's reply. I ran no
interactive session, where RES-0263 reads the documentation as running a
subagent in the background by default with a smaller built-in tool set.

The plugin held one agent, `agents/router.md`, whose front matter set
`name: router`, a one-sentence description and `tools: Read, Grep, Glob`.

- In the first run the agent's body asked it to list the tools it held and then
  try to create `probe.txt`.
- In the second run it asked the agent to call Glob for `*.md`, call Grep for
  `wrold`, and try to write `probe.txt`, reporting each tool it invoked.
- The third run was a control: the second run's brief, with `Write` added to
  `tools`, so that the model's own choice not to write could be told from the
  tool being absent.

I read the stream's `init` event for the main session's tools and agents, each
`tool_use` event with its `parent_tool_use_id` to tell the subagent's calls from
the main session's, and the final `result` event for turns, cost and duration,
with the tokens written to and read from the cache, and the `tool_result` that
handed the agent's reply back, which carries the agent's own tool count and
duration. After each run I ran `git status --porcelain` in the scratch
repository. The streams stayed in a scratch directory that isn't kept, so the
events each finding rests on are quoted under "Observed events" below.

I didn't run Opus 5.5, a repository of realistic size, or a request that needs
the agent to read many files. I also didn't measure the main session classifying
under a skill with no dispatch.

## Findings

### The allowlist holds: the agent has Read, Grep and Glob and nothing that writes

In the first run the agent listed `Read`, `Grep` and `Glob` and replied that no
tool it held writes files, so it didn't create `probe.txt`. In the second it
called `Glob` with `*.md`, which returned `README.md`, and `Grep` with `wrold`,
which returned one file. It didn't invoke Write and said it held none. After
both runs `git status --porcelain` printed nothing and `probe.txt` didn't exist.

In the control run, with `Write` in `tools`, the agent called Glob and Grep as
before, then called Write, and `git status --porcelain` printed `?? probe.txt`.
The brief and the model were the same, so what stopped the write in the first
two runs was the allowlist and not the model's choice.

This is what RES-0263 read in the platform's documentation, that `tools` is an
allowlist, now observed for a plugin agent on this version.

### The main session lists no Grep or Glob, and the subagent has both

The main session's `init` event listed 31 tools, including `Read`, `Write`,
`Edit`, `Bash` and `Task`, and neither `Grep` nor `Glob`. The `init` list named
no tool `Agent`, yet every dispatch appeared in the stream as a `tool_use` named
`Agent`, so on 2.1.280 the listing and the call name the dispatch tool
differently. The subagent called both Grep and Glob. A plugin agent can hold a
tool the main session doesn't show, so a definition naming Grep and Glob isn't
broken on 2.1.280. If a later version drops them from subagents too, the same
definition leaves the agent Read alone, which still writes nothing but finds
files only by paths it already knows.

### One dispatch cost 12.8 s to 19.7 s and USD 0.05 to USD 0.10 in a one-file repository

| Run | Turns | Duration  | Cost       | Cache written | Cache read | Agent's duration | Agent's tokens |
| --- | ----- | --------- | ---------- | ------------- | ---------- | ---------------- | -------------- |
| 1   | 2     | 12,755 ms | USD 0.0964 | 14,238        | 49,932     | 3,292 ms         | 5,683          |
| 2   | 2     | 22,661 ms | USD 0.0528 | 1,810         | 62,560     | 10,566 ms        | 6,609          |
| 3\* | 2     | 38,276 ms | USD 0.0874 | not read      | not read   | 12,466 ms        | 6,976          |

\* Run 3 is the control, whose agent held `Write` and so isn't the router design.

The duration and cost are whole sessions, the main session's two turns
included, so they bound the dispatch from above in this repository. The agent's
own duration and tokens come from the `usage` block in the reply the platform
handed back, and give no cost. The session durations of runs 2 and 3 also include
3 s in which `claude -p` waited on standard input and printed a warning, so run
2 took about 19.7 s net of the wait. A router that reads the record
and the files a request touches reads more than one file, so a real repository
costs more. The first run cost more because it wrote 14,238 tokens to the cache
where the second wrote 1,810: the first session started with an empty cache.
The agent's own durations compare the dispatch best, because they leave out the
main session's turns and the wait: the second agent took 10.6 s against the
first's 3.3 s, about three times as long, and it made two tool calls where the
first made none. Two runs are too few to call either duration typical.

### The dispatch carries the output style's reply-shape block

The prompt the main session sent the agent carried the
`<rules name="the reply shape">` block in all three runs. The output style `meow-core` ships asks
for that in its rule R10, at `plugins/meow-core/output-styles/meow.md`: the
parent includes the block in any prompt that dispatches a subordinate agent,
because the agent never sees the style. `meow-core` was enabled on this machine.
The three agents treated it three ways:

- In the first run the agent reported its failure as cause, location and fix,
  which is the block's rule R2, without naming the block.
- In the second run the agent declined to follow the block, saying it arrived
  as conversation text and not from its configuration, and it answered "in
  plain form instead".
- In the third run the agent's reply led with each call and its result, which
  fits the block's rule R1, and said nothing about the block.

Only the second agent said what it did with the block, so whether the first and
third followed it or happened to match it can't be told from their replies. So
a router's brief arrives with the style's block wherever `meow-core` is active,
and one agent in three refused it outright.

## Conclusions

1. An agent that classifies must declare `tools` in its definition naming no
   tool outside `Read`, `Grep` and `Glob`, because that allowlist held on this
   version in a foreground dispatch from `claude -p`. A subset complies, since
   `Read` alone also writes nothing. Grep and Glob are allowed because a router
   has to find files whose paths the request doesn't name, and that reason is
   unmeasured: the probes told the agent to call them, and no run showed that
   classification needs to search. An instruction not to write only asks, which
   rests on RES-0053 and RES-0263: no run here told an agent that held `Write`
   not to use it.
2. A check on the definition must fail on any entry in `tools` outside `Read`,
   `Grep` and `Glob`, and on a definition with no `tools`, because those three
   are the only tools observed in an allowlist that left the work tree clean,
   and a subset of them passes. A list of tools
   to refuse would have to name `Edit`, `NotebookEdit`, `Bash`, the dispatch
   tool, which could hand the work to an agent that writes, and every MCP tool,
   and the platform already names the dispatch tool one way in `init` and
   another in the call.
3. The unit that ships the agent must state the Claude Code version on which the
   allowlist was last observed, because the platform sets which tools a subagent
   can hold, and 2.1.280 already gives a subagent tools its main session doesn't
   list. The unit must also state the dispatch mode it was observed in, because
   only a foreground dispatch from `claude -p` was, and an interactive session
   may run the agent in the background with a smaller tool set (RES-0263).
4. A design that routes through an agent must state the dispatch as a cost paid
   on every routed request, including a typo, and measure it on a realistic
   repository before claiming a figure, because the only figures here come from
   a one-file repository, and the session figures bound the whole session and
   not the dispatch.
5. A router's output format must be stated in its own definition, because the
   reply-shape block the output style adds to a dispatch arrives as conversation
   text, and one agent in three declined it outright while the other two left
   no sign whether they followed it.
6. A design that routes through an agent must state what the brief passes it,
   because the agent runs in its own context window and sees none of the
   conversation (RES-0263), and this record left
   unmeasured whether the hand-off loses context the classification needs.

## Observed events

Every run's `init` event gave `claude_code_version` as `2.1.280` and listed
these 31 tools for the main session:

```text
Task, Bash, CronCreate, CronDelete, CronList, DesignSync, Edit, EnterWorktree,
ExitWorktree, ListAgents, ListMcpResourcesTool, LSP, Monitor, NotebookEdit,
PushNotification, Read, ReadMcpResourceDirTool, ReadMcpResourceTool,
RemoteTrigger, ReportFindings, ScheduleWakeup, SendMessage, Skill, TaskStop,
ToolSearch, WebFetch, WebSearch, Workflow, Write,
mcp__plugin_context7_context7__query-docs,
mcp__plugin_context7_context7__resolve-library-id
```

Its agents included `probe:router`. The `tool_use` events, with the parent
each carried, and the `result` events were these:

| Run | `tool_use` events                                                                                        | `result`                                          |
| --- | -------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| 1   | `Agent` (no parent), `subagent_type: probe:router`, prompt `go` and the reply-shape block                | 2 turns, 12,755 ms, USD 0.0964; agent 0 tool uses |
| 2   | `Agent` (no parent), as in run 1; `Glob` `*.md` and `Grep` `wrold`, each with the `Agent` call as parent | 2 turns, 22,661 ms, USD 0.0528; agent 2 tool uses |
| 3   | As in run 2, then `Write` `probe.txt` with content `probe`, with the `Agent` call as parent              | 2 turns, 38,276 ms, USD 0.0874; agent 3 tool uses |

The agent's replies, as handed back, opened this way:

- Run 1: the three lines `Read`, `Grep` and `Glob`, then "No write-capable
  tool is available in this toolset, so probe.txt was not created."
- Run 2: "Write(probe.txt) — not invoked: no Write tool is available in my
  toolset (only Read, Grep, Glob)", and later "I did not adopt it as a binding
  output style. It arrived as plain conversation content".
- Run 3: "Write to .../repo/probe.txt succeeded".

## Sources

- Claude Code 2.1.280 on this machine, run 2026-09-28: the three sessions above,
  the control run among them, their `stream-json` output, quoted under
  "Observed events" because the streams weren't kept, and
  `git status --porcelain` afterwards.
- [Agent definitions](RES-0263-agent-definitions.md), read 2026-09-28 - the
  platform's documentation of `tools` as an allowlist.
- [`/meow:discover`](RES-0053-discover.md), read 2026-09-28 - the conclusions
  this record tests: classify on the repository, report first, write nothing.
