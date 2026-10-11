---
id: ADR-2950
artifact: adr
status: approved
revised: 2026-10-11
addresses: [REQ-4618, REQ-3526]
supersedes: []
---

# 2950. The prose reviewer and the research step run as cheap subagents, haiku on Claude Code and glm on Pi

## Decision

Two reading-heavy acts of the harness run as subagents on a cheap model tier,
and the session that dispatched them writes the artifact and runs the checks.

The prose reviewer keeps its subagent. On Claude Code,
`plugins/meow-prose/agents/prose.md` runs on haiku 5.5, where its front matter
named sonnet. On Pi the reviewer maps to a registered tool,
`meow-prose-review`, whose nested model call carries the reply shape and
prefers glm 5.3 flash; a model the `MEOW_NESTED_MODEL` environment variable
names goes first, so a person chooses what a review costs. The nested call
inlines the standard it reviews against, read from the package's own
`skills/writing/` at load, because a nested call reads no file and holds no
skill (REQ-4618).

The research step runs as a subagent. On Claude Code, `meow-flow` ships
`agents/researcher.md`, which the step dispatches with the question and the
sources the person named; the researcher reads the primary sources and returns
the draft, and the session writes the artifact from `paw template research`,
fills its front matter, runs `paw check` and stops at the gate. On Pi the
`meow-research` tool's nested call drafts from the material the session
gathers, because a nested call reads nothing: the session passes the record
template, the search results and the sources' text it read. Both run on the
cheap tier: haiku 5.5 on Claude Code, glm 5.3 flash on Pi (REQ-3526).

What works once accepted: a prose review costs a cheap call on either
platform, and the research step's reading happens outside the session's
context, so the session that carries the chain to its gate pays only for the
draft and the checks. What still doesn't: the cheap tier reads less carefully
than the session would, so a research draft can miss a source a dearer model
would have read, and the person at the research gate is the check that holds;
and the Pi researcher drafts from gathered material only, so it reads nothing
itself.

## Why

The two acts share a shape: they read more than they write, their output is
text a person reviews before anything depends on it, and their cost lands on
every use of the method. A dearer model reading the whole repository for a
research draft, or sonnet reviewing a short text, spends where the gate after
them holds the risk anyway. The router's removal (ADR-2930) left the nested
call machinery without a tenant; the reviewer and the researcher are the two
acts whose reading earns a separate context, and the model choices follow the
same tier on both platforms, which REQ-4614 asks of a unit's contract.

## Alternatives

| Option                          | Better at               | Why it lost                                                                                          |
| ------------------------------- | ----------------------- | ---------------------------------------------------------------------------------------------------- |
| The session researches itself   | Reads with full context | The reading fills the context the chain's later steps need, and pays the session's model rate        |
| A dearer model for the reviewer | Catches finer findings  | The gate after the review is the person, and the cheap tier's misses cost a reread, not a defect     |
| No Pi mapping for either        | Smaller packages        | REQ-4614 holds a unit's contract equal, and a review the platform can't run is a method half-shipped |

## What it costs

The reviewer and the researcher run on models that read less carefully, so a
finding or a source can be missed where the session would have caught it; the
person at the gate holds that. Each tool's description loads on every Pi turn,
and each agent's description on every Claude Code turn, both counted in the
units' budgets. The Pi reviewer's nested call carries the standard inline, so
a review costs the standard's tokens every time.

## What would reverse it

- If hand-run reviews on the cheap tier miss rules the dearer tier caught, on
  the prose eval cases, I would move the reviewer back to the session's model.
- If research drafts from the cheap tier lack sources the step's rules require,
  I would have the session gather more before the call, and failing that,
  research in the session again.

## Consequences

- `plugins/meow-prose/agents/prose.md` names haiku; `packages/meow-prose/`
  gains the extension, the module and the bundled prompts, and its minor
  version rises.
- `plugins/meow-flow/agents/researcher.md` is new; `steps/research.md` states
  the dispatch and the write-back; the Pi tool lives in
  `packages/meow-flow/extensions/flow.ts`.
- The `meow-router` tool, its module and its prompts are deleted in the same
  change (ADR-2930), and the module moves to `packages/meow-prose/`.
- Both units' budgets rise by the descriptions they add and drop what the
  router's cost.
- SPC-1300's mapping states the two pairs and no router.

## How I will know it was realised

1. A prose review on Pi answers with findings and names no dispatch, and the
   nested call's model is glm 5.3 flash where `MEOW_NESTED_MODEL` names
   nothing.
2. The prose agent on Claude Code runs on haiku, and a research dispatch on
   Claude Code returns a draft the session writes, checks and stops at the
   gate with.
3. The budget checks pass with the new descriptions counted.
4. Every requirement this decision addresses lands in one closed task.

## What this does not settle

- Which other steps earn a subagent, which waits for the two here to show
  whether the cheap tier holds.
- A review or a draft the person can't tell from the session's own work; the
  reply shape labels what a nested call says, and nothing more.
- The requirements step or any later step running subagentically.
