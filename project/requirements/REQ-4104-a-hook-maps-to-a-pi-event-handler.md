---
id: REQ-4104
artifact: requirement
status: approved
cites: RES-0340
---

# A Claude Code hook maps to a Pi event handler

Each `hooks.json` entry maps to a TypeScript event handler registered with
`pi.on()`. The mapping is: `SessionStart` to `session_start`, `PreToolUse`
with a Bash matcher to `user_bash`, `PreToolUse` with a tool matcher to
`tool_call`, and `PostToolUse` to `tool_result`. The handler produces the same
effect as the Claude Code hook: blocking, feedback or pass-through.

Rationale: Pi event handlers are the structural analogue of Claude Code hooks.
They compose in extension load order and can block, mutate or pass through.
The mapping preserves the guard semantics (commit guard, push guard, prose
gate, loop guard, governance guard) while using Pi's native event system.
