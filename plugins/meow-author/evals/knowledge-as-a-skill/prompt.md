---
name: knowledge-as-a-skill
description: A request for an agent that carries a language's idioms, which the write skill should turn into a skill.
tags: [delegation]
runs: 3
max_turns: 20
timeout_seconds: 600
expected_outcome: The session writes a skill under .claude/skills/ carrying the idioms, writes no agent definition, and says why the idioms ship as a skill.
---

Add a Claude Code agent to this repository, under `.claude/`, that carries the
idioms of Go this team writes by: wrap an error with `%w` and add what the
caller was doing, accept an interface and return a concrete type, and pass a
`context.Context` as the first argument of anything that blocks. I want the
session to write Go that way whenever it touches Go code. Write the file, then
report what you wrote in two sentences.
