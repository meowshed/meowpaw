---
id: REQ-3187
artifact: requirement
topic: prose-and-comments
class: functional
status: withdrawn
revised: 2026-10-03
elaborates: RES-0027
source: BUG-1230, and the repository owner's decision
verification: judgement
---

# REQ-3187

**Withdrawn by ADR-2390. Replaced by REQ-3740 and REQ-3742.**

It read: a program MUST block a text for breaking the writing standard only on
a rule that names its defect as one of three things: a phrase from a closed
list, a construct of Markdown syntax, or an argument of the command that
publishes the text.

It kept the gate to the three exact rules, so every other rule of the standard
reached the reader unchecked until review. RES-0330 shows a program can call a
model for the rules that need judgement and still own the verdict, by
confirming each span and blocking only where two judgements agree. REQ-3740
keeps the three exact rules with the program, and REQ-3742 names which other
rules a model may judge.
