---
id: REQ-3526
artifact: requirement
topic: the-method
class: functional
status: approved
verification: static
elaborates: RES-0001
revised: 2026-10-11
---

# REQ-3526

The research step runs as a subagent on the cheap model tier: haiku 5.5 on
Claude Code, glm 5.3 flash on Pi. The step dispatches the researcher with the
question and the sources the person named; the researcher reads the primary
sources and returns the draft; the session writes the artifact from
`paw template research`, fills its front matter, runs `paw check` and stops at
the gate. On Pi the nested call drafts from the material the session gathers,
because a nested call reads nothing, and the session passes the record
template, the search results and the sources' text it read.
