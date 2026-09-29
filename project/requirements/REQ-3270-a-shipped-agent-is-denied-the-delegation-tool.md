---
id: REQ-3270
artifact: requirement
topic: delegation
class: functional
status: approved
revised: 2026-09-29
elaborates: RES-0016, RES-0263, RES-0284
verification: static
---

# REQ-3270

Every agent a unit of the harness ships, packs included, MUST declare a tool
list that withholds the delegation tool, so it can't dispatch a subagent
through the delegation tool, whatever its instructions say. The list is present, holds no `*`,
and names neither `Agent` nor its earlier name `Task`, alone or with a
restriction such as `Agent(worker)`.

Nested delegation is where cost and incoherence grow without a matching gain
(RES-0016), and a tool the agent doesn't hold is enforcement where an
instruction is only context. RES-0284 found that a missing list and `*` both
grant every tool, that the platform most likely reads `Task` as `Agent`, so
the list bans both, that a restricted entry still delegates, and that a plugin
can't set the session's nesting depth, so the delegation tool has to be
withheld agent by agent. `disallowedTools` doesn't replace the list, because
RES-0284 found only that the loader reads it, not what it does at a dispatch.

Two other paths to nested work are outside this requirement, and nothing
enforces against them yet: a skill with `context: fork` run through the
`Skill` tool, and a shell tool starting another model session. Neither
RES-0263 nor RES-0284 read whether either delegates from inside a subagent.
