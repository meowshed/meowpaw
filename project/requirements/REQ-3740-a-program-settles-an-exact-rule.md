---
id: REQ-3740
artifact: requirement
topic: prose-and-comments
class: functional
status: approved
revised: 2026-10-03
elaborates: RES-0330
source: the repository owner's request, and BUG-1230
verification: static
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3740

The gate MUST settle each rule that names its defect as a phrase from a closed
list, a construct of Markdown syntax or an argument of the publishing command
with a program that makes no model call for it.

A program gives such a rule the same answer every time, and a model asked to
judge one named phrases the text didn't hold (BUG-1230). This keeps what
REQ-3187 asked of the three exact rules, and leaves the other rules to
REQ-3742.
