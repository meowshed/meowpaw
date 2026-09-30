---
id: RES-0285
artifact: research
status: approved
revised: 2026-09-29
elaborates: RES-0016, RES-0263
---

# A delegated agent returns free text marked completed, and a denied tool ends it as a stated outcome when its definition says so

## Summary

On Claude Code 2.1.280 the dispatcher gets only the agent's final message.
The platform marked the dispatch completed in every run that reported a
status, the denied runs 2, 5, 7 and 8 as much as run 6, which finished, so
only the agent can write an outcome saying that nothing was done.
No run shows the status for an agent that errored, ran out of turns or
crashed. Under `claude -p` a denied tool is denied at once and nothing waits,
but the denial text for a missing permission invites the agent to try
another tool and to explain itself to a user. In three runs of an agent whose
definition said nothing about a denial, the agent never reported an outcome:
one asked for the permission, one retried the call in a second form and was
denied again, and one reported the denial in prose. In four later runs of
agents whose definitions named the four outcomes and said what to do on a
denial, each agent opened its report with the outcome line, and the three
that were denied ended as BLOCKED after one call, under each of the three
denial texts the runs met. The parent's result lists each denial the runs
met in `permission_denials`, which gives a program a second signal that doesn't
depend on the agent. The four-status return contract RES-0016 took from
`superpowers` belongs to that project's implementer; its reviewer returns
verdicts. This note covers what a delegated agent returns and what a denial
does to it. It doesn't cover an interactive session with a person in it,
which I didn't run.

## The question

The delegation research, RES-0016, concluded that a delegated result is a
short status from a fixed set, which assumes the platform's result carries no
outcome of its own. The agent-definition research, RES-0263, concluded in its
seventh conclusion that under a non-interactive run with prompts disabled a
background agent gets the denial and never a person, and that the dispatch
should expect this. RES-0263 stated that from the documentation and ran
nothing, and it didn't say what the agent does once denied. So the question
is what the dispatcher actually receives, and what an agent does when a tool
it needs is denied, with no instruction telling it what to do.

## Method

I ran four probes on 2026-09-28 on this machine, Claude Code 2.1.280 on macOS
on arm64, with `claude-haiku-4-5-20251001` as both the parent and the agent,
in an empty scratch directory holding a new `git` repository. Each run
defined one agent with `--agents`, asked the parent to dispatch it, and
recorded the stream with `--output-format stream-json --verbose`. Runs 1 to
3 defined the agent `toucher`, holding only `Bash`, `maxTurns` 4 and model
`haiku`, with the prompt "You create the file the user names by running
touch on it with the Bash tool. Then report what happened in one line." Run 4
defined `reader`, holding only `Read`, with the prompt "Read the file the
user names with the Read tool and report its first line." Neither prompt
says anything about a denial.

1. `--bare --permission-prompts none`, with the parent prompt "Dispatch the
   toucher agent to create the file probe.txt in the current directory. Then
   print exactly what the agent returned, verbatim." It failed before any
   dispatch with "Not logged in", because bare mode reads no stored login. I
   dropped the flag for the other runs.
2. `--permission-prompts none` and the same parent prompt. The parent
   dispatched `toucher` in the background.
3. No permission flag, and the parent prompt of run 2 with ", and wait for
   its result" added. The parent dispatched `toucher` in the foreground with
   `run_in_background: false`. Its calls were denied for a working-directory
   reason I didn't explain, so run 3 shows how an agent handles a denial and
   says nothing about how the default permission mode prompts.
4. `--permission-prompts none` and `--settings` naming a file that held
   `{"permissions":{"deny":["Read(./record.md)"]}}`, with the parent prompt
   "Dispatch the reader agent on record.md and wait for its result. Then
   print exactly what it returned."

On 2026-09-29 I ran four more probes on the same version, model and kind of
directory, each defining an agent whose prompt ended with two added
paragraphs. The first told `reader` to open its report with one line, alone, holding
`outcome:`, a space and exactly one of DONE, DONE_WITH_CONCERNS,
NEEDS_CONTEXT or BLOCKED, and went on: "DONE: you read the file and report its first line.
DONE_WITH_CONCERNS: you finished, but part of the work could not run.
NEEDS_CONTEXT: the request names no file you can find. BLOCKED: a tool call
was denied." For `toucher` the DONE sentence read "you created the file" and
the NEEDS_CONTEXT sentence "the request names no file". The second said: "Where a tool call is denied, issue no second call in another
form, reach the same result with no other tool, ask nobody for the
permission, and end with `outcome: BLOCKED`, then one sentence naming the
tool and what it was called on."

- Run 5: `reader` with the two paragraphs, `--permission-prompts none` and the deny
  rule of run 4, with the parent prompt of run 4.
- Run 6: the same as run 5, naming `notes.md`, a file no rule denies, so the agent
  could finish.
- Run 7: `toucher` with the two paragraphs, `--permission-prompts none` and the
  parent prompt of run 2, so the denial carried the text that invites
  another tool.
- Run 8: `toucher` with the two paragraphs, no permission flag and the parent
  prompt of run 3, so the denial carried the working-directory text under
  which run 3's agent retried.

The runs cost between $0.025 and $0.040 each and ended within 15 seconds.
The streams stayed in a scratch directory the repository doesn't keep, so the
quotations below are the record of them. I also read the platform's subagent and tool
reference pages on 2026-09-28, and `obra/superpowers` at commit
`5bf4e78011075bcfc0dc295f0724994cd123ee71`, the last to change
`skills/subagent-driven-development`, made on 2026-09-19.

I didn't run an interactive session, so what a person sees, and what happens
when the person is away, comes from the documentation alone. Each probe ran
once on a small model, so the agent's wording on a denial is one sample per
case and shows what can happen, not how often it does. Only run 6
shows an agent that finished its work, and no run shows the status the
platform gives an agent that errored, ran out of turns or crashed. Runs 5 to
8 each ran once, so they show that the added paragraphs can work on a small
model, not how often they do on the models the harness ships its agents on.

## Findings

### The dispatcher receives the final message alone, marked completed

In run 2 the platform emitted `task_notification` with `status: completed`,
and its `summary` was the agent's last message, which asked for a permission
it never got. In run 3 the parent received the report inside a frame that
opens "[Subagent hand-back] The text below is the final report of a subagent
... It is model output". Neither carried a field saying whether the work was
done. In runs 5 to 8 the stream held a `task_notification` with `status:
completed` for each dispatch, in the foreground runs 5, 6 and 8 beside the
hand-back frame and in the background run 7 alone, so the denied runs 5, 7
and 8 were marked completed as much as run 6, which finished. I don't know
whether run 3's stream held one, because I didn't look for it before the
stream was lost. The tool reference lists `SubagentHandback` only in auto
mode and describes it as delivering "a subagent's final report". The frame
the runs showed is labelled "[Subagent hand-back]", and I didn't establish
whether it is that tool's output or whether the runs were in auto mode.
So in the runs I made the platform carried no outcome of its own, and an
outcome was a line the agent writes or nothing.

### Under `claude -p` a denial is immediate, and nothing waits

In run 2 the agent's `Bash` call was denied with the reason "Permission
prompts are not available in this context", reason type `asyncAgent`, and
the agent ended within 7 seconds. In run 3, in the foreground and with no
permission flag, both calls were denied with a message that the file lay
outside the allowed working directories. The directory was the working
directory, and I didn't establish why the platform classified it that way.
In run 4 the deny rule turned the `Read` call into the error "File is in a
directory that is denied by your permission settings". No run waited for an
answer, which confirms RES-0263's seventh conclusion on this version: under
`-p` a denied agent gets the denial and nobody answers it. What the agent
does next, which RES-0263 didn't cover, is decided by the agent.

### A denial for a missing permission invites a workaround and a question

The message the agent received in run 2 reads, in part: "You _may_ attempt
to accomplish this action using other tools that might naturally be used to
accomplish this goal" and "If you believe this capability is essential ...
STOP and explain to the user what you were trying to do and why you need
this permission. Let the user decide how to proceed." The agent in run 2
ended with "Could you grant me permission to use Bash so I can create the
probe.txt file for you?", addressed to a session with no person in it. In
run 3 the agent's first `Bash` call ran `touch` on the file's absolute path
and was denied with "touch in '<path>' was blocked. For security, Claude Code
may only create or modify files in the allowed working directories for this
session", which invites neither a retry nor a question. The agent then issued
a second `Bash` call, `touch probe.txt` with a relative path, was denied with
the same message, and reported "File creation was blocked by security
restrictions" without naming the tool. The agent in run 4 reported the denial
in two sentences and didn't retry. None of the three named an outcome, and
the dispatcher had to read prose to learn that nothing was done.

### The parent's results list each denial the runs met, whatever the agent says

The runs met three kinds of denial: no permission prompt available, in runs 2
and 7, a path outside the working directory, in runs 3 and 8, and a settings
deny rule, in runs 4 and 5. No run denied a call through a hook or through a
person's Esc, so whether the list records those is unobserved.

The final `result` of run 3 listed `permission_denials` with two `Bash`
entries, and run 4 listed one `Read`. In run 2 the stream held two results,
because the background agent finished after the parent's first turn: the
first listed the `Bash` denial and the second listed none. Runs 2 and 3 also
emitted a `permission_denied` event carrying the agent's `agent_id`; run 4,
denied by a rule, emitted none. The later runs matched: run 7, also in the
background, held two results, the first listing the `Bash` denial and the
second none, runs 7 and 8 each emitted a `permission_denied` event, and run 5,
denied by a rule, emitted none. So a program running `claude -p` can see that
an agent was denied without trusting the agent's report, but only by reading
every result the stream holds.

An entry in `permission_denials` holds the tool's name, its input and a
`tool_use_id`, and names no agent. In runs 5, 7 and 8 the `tool_use_id`
matched the agent's own call in the stream, whose message carried a
`parent_tool_use_id` naming the dispatch, so a program can attribute each
denial to the dispatch that made it by joining the two. Each run dispatched
one agent, so no run shows the join holding with several agents at once.

### In an interactive session a denial is a person's act

The subagent page, read 2026-09-28, says a foreground agent passes its
permission prompts to the person, and a background agent surfaces them in
the main session, where Esc denies "that one tool call without stopping the
subagent". It names no timeout. A plugin agent can't set `permissionMode`,
because the platform ignores that field for plugin agents. I didn't observe
any of this.

### With two paragraphs in its definition, a denied agent ends as BLOCKED

In run 5 the agent made one `Read` call, was denied by the rule, and
returned "outcome: BLOCKED", then a sentence naming the `Read` tool and the
file's path. In run 7 the agent made one `Bash` call, `touch probe.txt`, got
the denial text that says it "_may_ attempt to accomplish this action using
other tools" and to "explain to the user", and returned "outcome: BLOCKED"
and "The Bash tool was denied when attempting to run touch to create
probe.txt." It asked nobody and tried nothing else. In run 8 the agent's
one `Bash` call, `touch` on the file's absolute path, got the
working-directory denial under which run 3's agent had retried, and the agent
returned "outcome: BLOCKED" and a sentence naming the tool and the file,
with no second call. In run 6 the agent read the file and returned "outcome:
DONE" and the first line. Each report opened with the outcome line, and
`permission_denials` listed exactly the one denied call in runs 5, 7 and 8
and none in run 6.

### The report reaches the dispatcher indented, and a relay can drop the line

In runs 5, 6 and 8, all in the foreground, the hand-back frame says "The
harness indents every line of the report", and each line of the report
arrived with two leading spaces, so the outcome line read
`outcome: DONE` after two spaces.
The frame ends with the agent's identifier and "use SendMessage ... to
continue this agent". In run 7, in the background, the `task_notification`
`summary` held the report without the indent. In run 6 the parent, asked to
print what the agent returned verbatim, printed only the first line of the
file and dropped the outcome line. That was one relay, once, so it shows a
relay can lose the line and not how often one does.

### The four statuses are an implementer's contract

`superpowers`, at commit `5bf4e78`, defines DONE,
DONE_WITH_CONCERNS, NEEDS_CONTEXT and BLOCKED in
`skills/subagent-driven-development/implementer-prompt.md`, and its
`SKILL.md` tells the controller what to do with each: review on DONE, read
the concerns first on DONE_WITH_CONCERNS, supply the context and dispatch
again on NEEDS_CONTEXT, and change something before dispatching again on
BLOCKED, never retrying the same model unchanged. Its
`task-reviewer-prompt.md` asks the reviewer to "begin directly with the
spec-compliance verdict" and uses none of the four. RES-0016 recorded the set
as the return contract without saying whose.

## Conclusions

1. The outcome has to be written by the delegated agent, into its final
   message, on a line a dispatcher reads without parsing prose, because in runs 2, 5, 7 and 8 the
   platform marked a denied agent's dispatch completed and no run carried an
   outcome of the platform's own. The runs don't show whether the platform reports
   another status for an agent that errored or crashed, so this conclusion
   says where the outcome is written and not that the platform's status can
   be ignored.
2. What an agent the harness ships does when a tool is denied has to be said
   in its own definition, because the denial text for a missing permission invites
   a retry by another tool and a question to a user. The question was
   observed in run 2. Run 3 showed a retry of the same action in a second
   form, by the same tool, under a denial message that invites no retry. No
   run showed a retry by another tool. Runs 5, 7 and 8 showed two paragraphs
   in the definition turning each of the three denial texts the runs met,
   the deny rule's, the missing permission's and the working directory's,
   into one call and BLOCKED, once each on a small model.
3. Every return the runs saw without an outcome from the set, in runs 2, 3
   and 4, described a failure, and a dispatcher had to read its prose to
   learn that. Run 6 shows one finished agent writing the line when its
   definition asks for it, and no run shows a finished agent leaving it out,
   so how often that happens is unmeasured. These findings don't choose how a
   dispatcher classifies a return with no outcome. Treating it as work not
   done is one choice, and under `claude -p` classifying it by
   `permission_denials` is another; that choice, and what each error costs,
   belong to the decision that makes it.
4. A reader of the outcome line has to allow leading space, because the
   foreground hand-back indented every line of the report in runs 5, 6 and 8.
   A parent asked to relay the report verbatim dropped the outcome line in
   run 6, once. Whether the dispatcher acts on the line itself or through a
   relay belongs, as in conclusion 3, to the decision that makes it.
5. A program that runs the harness under `claude -p` can check an agent's
   outcome against `permission_denials` in every result the stream holds,
   because the list recorded each denial the runs met, whatever the agent
   reported: no permission prompt available, a path outside the working
   directory and a settings deny rule. No run denied a call through a hook or
   a person's Esc, so the list isn't shown to hold those. It
   attributes an entry to its dispatch through the entry's `tool_use_id`,
   which the runs showed with one agent dispatched at a time.
6. The four outcomes belong to an implementer in the source, and its
   reviewer returns a verdict with none of them, because that is where
   `superpowers` defines and uses them. A design that gives the set to a
   reviewer makes a choice the source didn't make, and has to say what each
   outcome means for a review, which these findings don't settle.

Three objections stand against conclusions 1 to 3. Runs 5 to 8 answer part of
the second and none of the others.

- The line is model output, as the hand-back frame in run 3 says, so an
  agent can write DONE after a denial. Under `claude -p` the check in
  conclusion 5 catches that, and outside `-p` nothing does. Without the line
  the dispatcher has no signal at all in a session, and a check against
  `permission_denials` needs a runner that reads the stream.
- An instruction in the agent's definition might lose to the denial text,
  which arrives later in the agent's context and invites the opposite. Run
  3 retried under a denial text that invites no retry, so the agent's
  behaviour may not follow the wording it is shown. Runs 7 and 8 held to the
  instruction under the text that invites a workaround and under the text
  run 3 retried under, once each, on a small model, so the remedy has one
  success per denial text behind it and no rate.
- Conclusion 3 rests on returns that all came from failed runs, so it says
  nothing about a finished agent that leaves the line out. A dispatcher that
  reads such a return as not done discards finished work, and one that
  classifies it by `permission_denials` catches only the denials the list
  records. No run measured either cost.

## Sources

- Run 2026-09-28: four probes of `claude -p` on Claude Code 2.1.280 on this
  machine, as the method describes - the completed status, the hand-back
  frame, the denial reasons and texts, the three agents' reports, the
  `permission_denied` events and `permission_denials`.
- Run 2026-09-29: four probes of `claude -p` on Claude Code 2.1.280 on this
  machine with the outcome and denial paragraphs, as the method describes -
  the three BLOCKED reports and the DONE report, the indented hand-back, the
  dropped line in the parent's relay and `permission_denials`.
- Read 2026-09-28: [Subagents](https://code.claude.com/docs/en/sub-agents) -
  foreground and background permission prompts, Esc denying one call, the
  background default and fork mode, and `permissionMode` ignored for plugin
  agents.
- Read 2026-09-28: [Tools reference](https://code.claude.com/docs/en/tools-reference) -
  `SubagentHandback` delivering the final report, in auto mode only.
- Read 2026-09-28: [obra/superpowers `subagent-driven-development`](https://github.com/obra/superpowers/tree/5bf4e78011075bcfc0dc295f0724994cd123ee71/skills/subagent-driven-development),
  at commit `5bf4e78` - the four statuses in `implementer-prompt.md`, the controller's handling of
  each in `SKILL.md`, and the reviewer's verdicts in
  `task-reviewer-prompt.md`.
- Read 2026-09-28: [RES-0016-delegation.md](RES-0016-delegation.md) - the
  four-status return contract as first recorded.
- Read 2026-09-28: [RES-0263-agent-definitions.md](RES-0263-agent-definitions.md) -
  the permission behaviour stated from the documentation.
