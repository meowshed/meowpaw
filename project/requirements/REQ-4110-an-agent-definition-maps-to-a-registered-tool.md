---
id: REQ-4110
artifact: requirement
topic: pi-packages
class: functional
status: withdrawn
revised: 2026-10-11
verification: behavioural
elaborates: RES-0340
---

# REQ-4110

Withdrawn by ADR-2930, which deletes the router agent and the `meow-router`
tool it mapped to, and leaves no agent definition that maps to a Pi tool; a
later decision states the mapping when an agent ships.

The router agent (`agents/router.md`) and the skeptic agent become tools
registered by the meow-flow extension via `pi.registerTool()`. The tool's
`execute` function makes a nested model call with `ctx.modelRegistry.streamSimple()`,
constraining the model, effort, tool set and prompt to what the agent
definition's frontmatter declares. The tool returns the nested call's output
as its result.

Rationale: Pi has no agent-definition files. A registered tool with a nested
model call is the structural equivalent of a dispatched subagent. The tool can
declare `exposure: "codemode"` or `"direct"` to control when the model reaches
it, and its description replaces the agent's `description` for routing.
