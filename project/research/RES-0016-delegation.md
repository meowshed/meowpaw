---
id: RES-0016
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Delegation

## Summary

Delegation is for context isolation or independent tracks, never for size. The
brief is the source of requirements and the session history is not passed,
which three surveyed harnesses arrived at separately. Delegated agents do not
delegate, constraints are copied verbatim, and summarised nowhere, the return
is a short structured status, and review is a separate dispatch with a narrowed
tool set.

Research for how `meow-review` and `meow-loop` dispatch work to subordinate
agents. This is what the
practice looks like.

## Method

The published material on delegation patterns was fetched and read on
2026-09-20, alongside the surveyed harnesses' own descriptions of how they
dispatch work, which live in their repositories, where the articles describe
them second-hand.

Nothing was run. No delegation was measured, so the claim that isolation rather
than size is the right reason rests on what three harnesses do and why they say
they do it.

## What delegation actually buys

Context isolation, and it is the underappreciated half. A subtask runs in
the subordinate's own context; the orchestrator receives only the result, not
the intermediate reasoning. So a task decomposed across several subordinates
does not grow the orchestrator's context in proportion to its complexity.

That is the mechanism behind `superpowers`' multi-hour autonomous runs, and it
is why the report back must be short and structured: a
delegation that returns everything it read has bought nothing.

A narrowed tool set is the second. A subordinate has its own tools, and
a reviewer that cannot write is a reviewer that cannot quietly fix what it was
supposed to report.

## When not to delegate

The reported guidance is consistent, and it states these as rules because the
failure mode is over-delegation - spawning agents for work that would have been
three tool calls:

- **No context pressure, no decomposition needed.** Work confined to one small
  file does not need a subordinate.
- **The marginal quality gain is below the marginal cost.** Debate-style
  multi-model arbitration is measured at roughly 2.5x the single-model cost; it
  has to buy something.
- **The user asked you to do it.** Delegating work someone asked _you_ for is a
  different answer to the question they posed.

Against that, delegation both improves coding performance and reduces cost in
measurements _when the decomposition is real_ - so the test is whether the task
is genuinely self-contained, and its size decides nothing.

## The topology

Supervisor, one level deep, is the 2026 production default, and Claude
Code, LangGraph and the OpenAI Agents SDK converge on it. Nested delegation -
subordinates that delegate - is where cost and incoherence grow without a
matching gain.

For this harness that means: the chain's commands delegate; delegated agents do
not.

## What a brief contains

`superpowers`' dispatch prompt, which is the most developed in the survey:

- **The task brief**, as the single source of requirements - extracted, not
  narrated. - **The report file path**, so the result has a place to go. -
  **Only the interfaces this task touches**, plus decisions resolved earlier. -
  **The global constraints, verbatim**, copied and summarised nowhere. - And
  explicitly **not** the session history.

The stated rule: "A dispatch prompt describes one task, not the session's
history." That is a sufficient brief in one sentence.

The return contract is a fixed status set: DONE, DONE_WITH_CONCERNS,
NEEDS_CONTEXT, BLOCKED, and no prose. A fixed set is what lets the orchestrator
decide without reading.

## Review is a separate dispatch

Review is a separate delegation, and every harness that reviews agrees: the reviewer did not do the
work, receives the brief and the diff against a recorded base, and returns two
verdicts.

`cc-sdd` adds the case where they disagree: after two rejections, an auto-debug
pass **in a clean context**. An implementer and a reviewer arguing inside one
context converge on nothing, because the context now contains both positions
and the argument.

## Bounding repair

`superpowers` caps the fix loop at five rounds, escalates rounds four and five
to a fresh implementer on a more capable model, keeps a **ledger** of addressed
and open findings that survives compaction, and adjudicates the residue rather
than retrying it.

Repair takes the bound. The ledger is the same mechanism as the evidence
ledger, and for the same reason: conversation memory does not survive
compaction, so progress lives in a file.

## Model and effort selection

The platform exposes `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`
and `isolation: "worktree"` on an agent definition.

Two uses transfer: a **narrow tool set** for a reviewer, and **escalation**

- a harder model for the rounds after the first attempts failed, which is
  `superpowers`' pattern and costs nothing until it is needed.

`isolation: "worktree"` is what makes parallel implementers safe, and it is why
[decision 0003] can leave worktree management to a tool pack: the platform
already supplies the case that mattered.

## Conclusions

1. Delegate for context isolation or independent tracks, and never because a
   task is large. 2. One level deep. Delegated agents do not delegate. 3. The
   brief is the source of requirements; the session history is not passed. 4.
   Constraints are copied verbatim, never summarised. 5. The return is a short
   structured status from a fixed set. 6. Review is a separate dispatch with a
   narrowed tool set. 7. Disagreement resolves in a clean context, and never
   inside the argument. 8. Repair is bounded, escalates, and keeps a ledger.

## Sources

- [Subagents: complete guide to multi-agent AI coding (2026)](https://www.morphllm.com/subagents),
  read 2026-09-20 - isolated context windows, restricted tool permissions, and
  the orchestrator receiving only the result.
- [AI agent delegation patterns: four best architectures for 2026](https://fast.io/resources/ai-agent-delegation-patterns/),
  read 2026-09-20.
- [Multi-agent orchestration: 5 patterns that work in 2026](https://www.digitalapplied.com/blog/multi-agent-orchestration-5-patterns-that-work),
  read 2026-09-20 - supervisor, one level deep, as the production default across
  Claude Code, LangGraph and the OpenAI Agents SDK.
- [AI agent subagent orchestration: when to spawn vs when to do it yourself](https://dev.to/bobrenze/ai-agent-subagent-orchestration-when-to-spawn-vs-when-to-do-it-yourself-4opg),
  read 2026-09-20 - the not-delegating rules, and the cost test.
- [Spring AI agentic patterns: subagent orchestration](https://spring.io/blog/2026/01/27/spring-ai-agentic-patterns-4-task-subagents/),
  read 2026-09-20 - context isolation stated as the underappreciated benefit.
- [DecisionBench: a benchmark for emergent delegation in long-horizon agentic workflows](https://arxiv.org/pdf/2605.19099),
  read 2026-09-20.
- [obra/superpowers `subagent-driven-development`](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md),
  read 2026-09-20 - the dispatch prompt's contents, the four-value return
  contract, the five-round fix loop with escalation, and the ledger.
- [Claude Code plugin reference](https://code.claude.com/docs/en/plugins-reference),
  read 2026-09-20 - agent frontmatter: `model`, `effort`, `maxTurns`, `tools`,
  `disallowedTools`, `isolation: "worktree"`.
