---
id: REQ-3186
artifact: requirement
topic: prose-and-comments
class: functional
status: withdrawn
revised: 2026-09-28
elaborates: RES-0027
verification: judgement
---

# REQ-3186

**Withdrawn. Replaced by REQ-3187.**

It read: the writing standard MUST NOT be enforced by a pattern over the text.

It also forbade a program matching a rule that names its defect exactly, such
as a phrase from a closed list or a line of Markdown syntax, which asks for no
guess. That left the gate's three exact rules to a model, which blocked texts
for phrases they didn't hold (BUG-1230). REQ-3187 keeps the ban on a pattern
that guesses at meaning and lets a program hold an exact rule.
