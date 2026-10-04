---
id: REQ-4108
artifact: requirement
status: approved
cites: RES-0340
---

# The output style is injected by a before_agent_start handler

The reply shape that `meow-core` provides as `output-styles/meow.md` is
injected into the system prompt by an extension's `before_agent_start` event
handler, adding it to `event.systemPromptOptions.guidelines`. No Pi output
style mechanism exists; the extension provides the equivalent.

Rationale: Pi has no output-style directory or `force-for-plugin` field. The
`before_agent_start` event is the point where an extension can modify the
prompt the model receives. Injecting the reply shape there ensures every model
call sees it, which is what `force-for-plugin: true` does in Claude Code.
