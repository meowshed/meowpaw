---
id: REQ-4102
artifact: requirement
topic: pi-packages
class: functional
status: withdrawn
revised: 2026-10-04
elaborates: RES-0340
verification: behavioural
---

# REQ-4102

**Withdrawn by ADR-2790. Replaced by REQ-4132.**

It read: every skill a Claude Code plugin provides as `SKILL.md` is carried
unchanged in the Pi package, because the same format loads on both
platforms.

BUG-1401 found the copies naming `${CLAUDE_SKILL_DIR}` in forty places, a
variable Pi never sets, so the method's very first command answered not
found. REQ-4132 states what holds in its place: the skill is carried with
one phrasing alone adapted — its binary named by its plain command and its
files relative to the skill's own directory — which serves both platforms,
because Claude Code puts a plugin's `bin/` on PATH natively.
