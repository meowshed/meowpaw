---
id: REQ-4132
artifact: requirement
topic: pi-packages
class: functional
status: approved
revised: 2026-10-04
verification: behavioural
elaborates: RES-0340, BUG-1401
---

# REQ-4132

A skill in a Pi package names its unit's binary by its plain command name,
`paw check` and not `${CLAUDE_SKILL_DIR}/../../bin/paw check`, and names a
supporting file relative to the skill's own directory, `steps/research.md`
and not `${CLAUDE_SKILL_DIR}/steps/research.md`. The package's extension
puts the package's `bin/` directory on the session's PATH at load, so the
plain name resolves; the platform tells the model where the skill lives, so
the relative file resolves.

Rationale: BUG-1401 found fourteen skills naming a variable Pi never sets,
so the model runs a literal string and the shell answers not found. A plain
command name is what Claude Code's own plugins resolve to as well, since
that platform puts a plugin's `bin/` on PATH, so one phrasing serves both.
