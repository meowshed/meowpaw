---
type: llm
focus: last_message
weight: 2
---

Judge whether the session shipped the idioms as a skill and not as an agent.

PASS when the report says it wrote a skill, such as a `SKILL.md` under
`.claude/skills/`, and wrote no agent definition, and gives a reason such as
knowledge needing no isolation or an agent paying for a fresh context on every
dispatch.

FAIL when the report says it wrote an agent definition, such as a file under
`.claude/agents/`, whether or not it also wrote a skill.
