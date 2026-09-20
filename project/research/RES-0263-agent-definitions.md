---
id: RES-0263
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0016, RES-0201
---

# Agent definitions

## Summary

The delegation research settled when to delegate and never said what the
delegate is. The platform now has two mechanisms that look alike and are not. A
subagent starts fresh with its own system prompt and its own tools, and a skill
forked into an agent inherits the parent's conversation. That difference
decides which one a reviewer may be, because a reviewer that inherits the
worker's context is a reviewer judging its own work. The definition also
carries a turn budget, a nesting depth of three where this method wants one,
and a worktree isolation flag that answers the parallel-work question directly.

Research for the agent definition as an artifact. It does not cover when to
delegate, which is [RES-0016-delegation.md](RES-0016-delegation.md), nor the
skill authoring surface, which is
[RES-0201-skill-authoring.md](RES-0201-skill-authoring.md).

## The question

The method dispatches review, verification and parallel implementation to
subordinate agents. Something has to define those agents: what they can see,
what tools they hold, which model runs them, and what stops them.

One document says delegated agents do not delegate. The platform's default
allows three levels. That disagreement alone paid for the research.

## Method

The platform's subagent documentation was fetched and read on 2026-09-20 for
the full frontmatter set, the comparison with forked skills, the nesting
behaviour, and the difference between foreground and background execution.

The sandboxing and hooks research already in this corpus supplied what a
subagent inherits from its parent that the subagent page does not mention.

Nothing was built. We defined and dispatched no agent, so the recommendations
here are design claims against a documented surface, and none of them is a
result.

## Findings

### Two mechanisms that look alike, and the difference decides the reviewer

A **subagent** runs in its own context window with its own system prompt, its
own tool access and its own permission settings, and returns a summary rather
than its working.

A **skill forked into an agent** is invoked like a skill, shares the parent's
system prompt, and inherits the parent conversation history.

The platform states the distinction as purpose: subagents isolate output and
context, while forked skills inject knowledge into a specific agent.

For this method the consequence is sharper than a preference. The verification
research established that an agent must not judge its own work, and that the
judge is not told which side it produced. Where that cannot be arranged, the
result is reported as self-assessed and never as a judgement.

A forked skill inherits the conversation that produced the work. So **a
reviewer is a subagent and cannot be a forked skill** - not because the
subagent is better at reviewing, but because the forked one has already seen
whose work it is.

A lens, a language's idioms or a writing standard is knowledge and needs no
isolation, so a forked skill carries it.

### The definition carries a budget, which the loop research wanted and did not have

`maxTurns` bounds the agentic turns before the subagent stops.

That is a per-dispatch ceiling the runner enforces, and nobody asks the model
to respect it. It is exactly the property the loop research identified as
necessary, and it used to be available only from the loop plugin. It means a
delegated task cannot run away, independently of whatever budget the outer run
is keeping.

The related fields make the dispatch cheap as well as bounded: `model` routes
to a smaller model, and `effort` overrides the session's level. A high-volume
search delegated to a small model at low effort is a different cost from the
same search in the main conversation.

### The nesting default is three and this method wants one

By default a subagent spawns its own subagents up to three layers below the
main conversation. At the limit the platform withholds the delegation tool, so
the subagent does the work itself. The depth is configurable through an
environment variable.

The delegation research concluded that delegated agents do not delegate, and
the reasons have not changed. A brief written for one level is not a brief at
two, and the return contract degrades at each hop.

So the harness sets the depth and accepts no default. That is a setting the
harness ships and no instruction it writes, which matters: an instruction is
context and a setting is enforcement.

### Background is the default, and it is the same process

In an interactive session subagents run in the background by default: they run
concurrently, surface permission prompts in the main session, and hold a
smaller built-in tool set. Foreground subagents block until they finish and
have full tool access.

Two consequences that are easy to miss.

They run in the same process. Combined with the sandboxing finding that
subagents share the parent's sandbox configuration, that means delegation does
not widen the boundary and does not narrow it either. A delegated agent is not
a sandbox.

Permission prompts surface in the main session. Under a non-interactive run
with prompts disabled, a background subagent that needs a permission gets the
denial and never a person, which is the correct behaviour and something the
dispatch expects rather than discovers.

### The tool allowlist is the honest part of the contract

`tools` is an allowlist and `disallowedTools` is a denylist. The review
research already requires a reviewer to be dispatched with a narrowed tool set,
and this is where that stops being a wish.

A reviewer with no write tools cannot edit the thing it is reviewing, which
enforces the read-only discipline that an instruction only describes. That is
the single most valuable field in the definition for this method, because the
instruction form of the same rule is the one most likely to be forgotten under
pressure.

### Three fields answer questions other documents in this corpus left open

`isolation: worktree` runs the agent in its own git worktree. The delegation
and worktree research both concluded that parallel work needs a working
directory per agent, and this declares it, so nothing has to arrange it.

`omitClaudeMd` skips the instruction files. A high-volume searcher does not
need the constitution and pays for it on every dispatch; a reviewer judging
conformance to the project's standards needs exactly that. So it is a per-agent
decision with a clear test: does this agent judge against the project's rules.

`skills` preloads skill content into the subagent. That is how a reviewer
gets the language pack's idioms without the main conversation paying for them,
and it is the mechanism that makes a narrow, well-equipped reviewer cheap.

### Hooks in a definition inherit the trust caveat

An agent definition may carry lifecycle hooks. The hooks research already
records that hooks declared in skill or subagent frontmatter follow the
workspace trust rule, and do not run in a non-interactive session where the
folder was never trusted.

So a hook in an agent definition is enforcement where the workspace is trusted
and absent otherwise, which is the same layered conclusion: the hook enforces,
the gate checks, the instruction explains.

### Where definitions live, and what that means for a plugin

Definitions live at user level or project level, and a plugin ships them in its
own directory.

The plugin reference adds the detail that matters for the harness: a project or
user definition overrides a same-named plugin definition. So a repository can
replace the harness's reviewer with its own, which is the right default and
makes the harness's own definitions a starting point that guarantees nothing.

## Conclusions

1. A reviewer is a subagent, never a forked skill, because a forked skill
   inherits the conversation that produced the work and has already seen whose
   work it is. 2. Knowledge is a forked skill and never a subagent, since a
   lens or a language's idioms are injected into the work and need no
   isolation. 3. Every dispatched agent declares `maxTurns`, which is a ceiling
   the runner enforces, and nobody asks the model to respect it. 4. A reviewer
   is dispatched with no write tools, which turns the read-only discipline from
   an instruction into a restriction. 5. The harness sets the nesting depth to
   one and accepts no default of three, because a brief written for one level
   is not a brief at two, and a setting is enforcement where an instruction is
   context. 6. Delegation does not change the sandbox. Subagents run in the
   same process and share the parent's sandbox configuration, so a delegated
   agent is not an isolation boundary. 7. A background subagent's permission
   request reaches the main session, so under a non-interactive run with
   prompts disabled it is denied and nobody answers it, and the dispatch
   expects that. 8. Parallel implementation declares worktree isolation, so
   nothing has to arrange a working directory separately. 9. Whether an agent
   loads the project's instructions is a per-agent decision, decided by whether
   it judges against the project's rules. 10. A narrow agent preloads the
   skills it needs, so the main conversation does not pay for knowledge only
   the delegate uses. 11. A hook in an agent definition is enforcement only
   where the workspace is trusted, and is absent in a non-interactive run, so
   it is layered rather than relied on. 12. A repository may replace any agent
   the harness ships, since a project definition overrides a same-named plugin
   one, and the harness's definitions are a starting point. 13. Model and
   effort are part of the dispatch decision, because a high-volume search on a
   small model at low effort is a different cost from the same work in the main
   conversation.

## Sources

All read 2026-09-20.

- [Subagents](https://code.claude.com/docs/en/sub-agents) - subagents as
  isolated context windows with custom system prompts, independent tool access
  and permission settings; the frontmatter set including `tools`,
  `disallowedTools`, `model`, `permissionMode`, `memory`, `maxTurns`, `skills`,
  `mcpServers`, `hooks`, `background`, `omitClaudeMd`, `effort`, `isolation`
  and `initialPrompt`, with only name and description required; the comparison
  with a skill run under `context: fork`, where the subagent starts fresh with
  its own prompt and the forked skill inherits the parent conversation and
  shares its system prompt; the three-layer default nesting depth, the
  withheld delegation tool at the limit, and the variable that changes it;
  background execution as the interactive default with a restricted tool set,
  permission prompts surfacing in the main session, and subagents running in
  the same process; and definitions at user and project level.
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference) - that
  project and user definitions override same-named plugin definitions.
- [RES-0070-who-verifies.md](RES-0070-who-verifies.md) - that an agent must not
  judge its own work, that a judge should not be told which side it produced,
  and that where that cannot be arranged the result is self-assessed.
- [RES-0016-delegation.md](RES-0016-delegation.md) - one level deep, the brief
  as the source of requirements, and the narrowed tool set for review.
- [RES-0203-hooks.md](RES-0203-hooks.md) - that frontmatter hooks follow the
  workspace trust rule and do not run in a non-interactive session.
- [RES-0074-unattended-mode.md](RES-0074-unattended-mode.md) - that subagents
  share the parent's sandbox configuration, and the behaviour of permission
  requests when prompts are disabled.
