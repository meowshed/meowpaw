---
id: REQ-4102
artifact: requirement
status: approved
cites: RES-0340
---

# A Pi skill is the same SKILL.md the Claude Code plugin carries

Every skill that a meowpaw plugin provides as `skills/<name>/SKILL.md` is
carried unchanged in the Pi package's `skills/` directory. Pi's skill discovery
loads the same file by the same progressive-disclosure mechanism: the
description appears in the system prompt, and the full instructions load on
invocation.

Rationale: The Agent Skills specification that Pi implements is the same format
Claude Code uses. The content is portable. Rewriting would gain nothing and
would drift from the tested prompt.
